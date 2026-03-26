import pandas as pd 
import re
from Config import *


def get_input_data()->pd.DataFrame:
    df1 = pd.read_csv(Config.APPGALLERY_PATH, skipinitialspace=True)
    df1.rename(columns={'Type 1': Config.TYPE1, 'Type 2': Config.TYPE2, 'Type 3': Config.TYPE3, 'Type 4': Config.TYPE4}, inplace=True)
    df2 = pd.read_csv(Config.PURCHASING_PATH, skipinitialspace=True)
    df2.rename(columns={'Type 1': Config.TYPE1, 'Type 2': Config.TYPE2, 'Type 3': Config.TYPE3, 'Type 4': Config.TYPE4}, inplace=True)
    df = pd.concat([df1, df2])
    df[Config.INTERACTION_CONTENT] = df[Config.INTERACTION_CONTENT].values.astype('U')
    df[Config.TICKET_SUMMARY] = df[Config.TICKET_SUMMARY].values.astype('U')
    
    # Filter out missing values in type columns
    for col in Config.TYPE_COLS:
        df = df.loc[(df[col] != '') & (~df[col].isna()),]
        
    df.reset_index(drop=True, inplace=True)
    
    # Create chain labels
    df['y_chain_1'] = df[Config.TYPE2].astype(str)
    df['y_chain_2'] = df[Config.TYPE2].astype(str) + Config.CHAIN_SEP + df[Config.TYPE3].astype(str)
    df['y_chain_3'] = df[Config.TYPE2].astype(str) + Config.CHAIN_SEP + df[Config.TYPE3].astype(str) + Config.CHAIN_SEP + df[Config.TYPE4].astype(str)
    
    return df

def de_duplication(data: pd.DataFrame):
    data["ic_deduplicated"] = ""

    cu_template = {
        "english":
            [r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) Customer Support team\,?",
             r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE is a company incorporated under the laws of Ireland with its headquarters in Dublin, Ireland\.?",
             r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE is the provider of Huawei Mobile Services to Huawei and Honor device owners in (?:Europe|\*\*\*\*\*\(LOC\)), Canada, Australia, New Zealand and other countries\.?"]
        ,
        "german":
            [r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) Kundenservice\,?",
             r"Die (?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE ist eine Gesellschaft nach irischem Recht mit Sitz in Dublin, Irland\.?",
             r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE ist der Anbieter von Huawei Mobile Services für Huawei- und Honor-Gerätebesitzer in Europa, Kanada, Australien, Neuseeland und anderen Ländern\.?"]
        ,
        "french":
            [r"L'équipe d'assistance à la clientèle d'Aspiegel\,?",
             r"Die (?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE est une société de droit irlandais dont le siège est à Dublin, en Irlande\.?",
             r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE est le fournisseur de services mobiles Huawei aux propriétaires d'appareils Huawei et Honor en Europe, au Canada, en Australie, en Nouvelle-Zélande et dans d'autres pays\.?"]
        ,
        "spanish":
            [r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) Soporte Servicio al Cliente\,?",
             r"Die (?:Aspiegel|\*\*\*\*\*\(PERSON\)) es una sociedad constituida en virtud de la legislación de Irlanda con su sede en Dublín, Irlanda\.?",
             r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE es el proveedor de servicios móviles de Huawei a los propietarios de dispositivos de Huawei y Honor en Europa, Canadá, Australia, Nueva Zelanda y otros países\.?"]
        ,
        "italian":
            [r"Il tuo team ad (?:Aspiegel|\*\*\*\*\*\(PERSON\)),?",
             r"Die (?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE è una società costituita secondo le leggi irlandesi con sede a Dublino, Irlanda\.?",
             r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE è il fornitore di servizi mobili Huawei per i proprietari di dispositivi Huawei e Honor in Europa, Canada, Australia, Nuova Zelanda e altri paesi\.?"]
        ,
        "portguese":
            [r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) Customer Support team,?",
             r"Die (?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE é uma empresa constituída segundo as leis da Irlanda, com sede em Dublin, Irlanda\.?",
             r"(?:Aspiegel|\*\*\*\*\*\(PERSON\)) SE é o provedor de Huawei Mobile Services para Huawei e Honor proprietários de dispositivos na Europa, Canadá, Austrália, Nova Zelândia e outros países\.?"]
        ,
    }

    cu_pattern = ""
    for i in sum(list(cu_template.values()), []):
        cu_pattern = cu_pattern + f"({i})|"
    cu_pattern = cu_pattern[:-1]

    # -------- email split template

    pattern_1 = r"(From\s?:\s?xxxxx@xxxx.com Sent\s?:.{30,70}Subject\s?:)"
    pattern_2 = "(On.{30,60}wrote:)"
    pattern_3 = r"(Re\s?:|RE\s?:)"
    pattern_4 = r"(\*\*\*\*\*\(PERSON\) Support issue submit)"
    pattern_5 = r"(\s?\*\*\*\*\*\(PHONE\))*$"

    split_pattern = f"{pattern_1}|{pattern_2}|{pattern_3}|{pattern_4}|{pattern_5}"

    # -------- start processing ticket data

    tickets = data["Ticket id"].value_counts()

    for t in tickets.index:
        #print(t)
        df = data.loc[data['Ticket id'] == t,]

        # for one ticket content data
        ic_set = set([])
        ic_deduplicated = []
        for ic in df[Config.INTERACTION_CONTENT]:

            # print(ic)

            ic_r = re.split(split_pattern, ic)
            # ic_r = sum(ic_r, [])

            ic_r = [i for i in ic_r if i is not None]

            # replace split patterns
            ic_r = [re.sub(split_pattern, "", i.strip()) for i in ic_r]

            # replace customer template
            ic_r = [re.sub(cu_pattern, "", i.strip()) for i in ic_r]

            ic_current = []
            for i in ic_r:
                if len(i) > 0:
                    # print(i)
                    if i not in ic_set:
                        ic_set.add(i)
                        i = i + r"\n"
                        ic_current = ic_current + [i]

            #print(ic_current)
            ic_deduplicated = ic_deduplicated + [' '.join(ic_current)]
        data.loc[data["Ticket id"] == t, "ic_deduplicated"] = ic_deduplicated
    data[Config.INTERACTION_CONTENT] = data['ic_deduplicated']
    data = data.drop(columns=['ic_deduplicated'])
    return data

def noise_remover(df: pd.DataFrame):
    noise = r"(sv\s*:)|(wg\s*:)|(ynt\s*:)|(fw(d)?\s*:)|(r\s*:)|(re\s*:)|(\[|\])|(aspiegel support issue submit)|(null)|(nan)|((bonus place my )?support.pt 自动回复:)"
    df[Config.TICKET_SUMMARY] = df[Config.TICKET_SUMMARY].str.lower().replace(noise, " ", regex=True).replace(r'\s+', ' ', regex=True).str.strip()
    df[Config.INTERACTION_CONTENT] = df[Config.INTERACTION_CONTENT].str.lower()
    noise_1 = [
        r"(from :)|(subject :)|(sent :)|(r\s*:)|(re\s*:)",
        "(january|february|march|april|may|june|july|august|september|october|november|december)",
        "(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
        "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        r"\d{2}(:|.)\d{2}",
        r"(xxxxx@xxxx\.com)|(\*{5}\([a-z]+\))",
        "dear ((customer)|(user))",
        "dear",
        "(hello)|(hallo)|(hi )|(hi there)",
        "good morning",
        "thank you for your patience ((during (our)? investigation)|(and cooperation))?",
        "thank you for contacting us",
        "thank you for your availability",
        "thank you for providing us this information",
        "thank you for contacting",
        "thank you for reaching us (back)?",
        "thank you for patience",
        "thank you for (your)? reply",
        "thank you for (your)? response",
        "thank you for (your)? cooperation",
        "thank you for providing us with more information",
        "thank you very kindly",
        "thank you( very much)?",
        "i would like to follow up on the case you raised on the date",
        "i will do my very best to assist you"
        "in order to give you the best solution",
        "could you please clarify your request with following information:"
        "in this matter",
        "we hope you(( are)|('re)) doing ((fine)|(well))",
        "i would like to follow up on the case you raised on",
        "we apologize for the inconvenience",
        "sent from my huawei (cell )?phone",
        "original message",
        "customer support team",
        "(aspiegel )?se is a company incorporated under the laws of ireland with its headquarters in dublin, ireland.",
        "(aspiegel )?se is the provider of huawei mobile services to huawei and honor device owners in",
        "canada, australia, new zealand and other countries",
        r"\d+",
        "[^0-9a-zA-Z]+",
        r"(\s|^).(\s|$)"]
    for noise in noise_1:
        #print(noise)
        df[Config.INTERACTION_CONTENT] = df[Config.INTERACTION_CONTENT].replace(noise, " ", regex=True)
    df[Config.INTERACTION_CONTENT] = df[Config.INTERACTION_CONTENT].replace(r'\s+', ' ', regex=True).str.strip()
    #print(df.y1.value_counts())
    good_y1 = df.y1.value_counts()[df.y1.value_counts() > 10].index
    df = df.loc[df.y1.isin(good_y1)]
    #print(df.shape)
    return df

def translate_to_en(texts:list[str]):
    import stanza
    from stanza.pipeline.core import DownloadMethod
    from transformers import pipeline
    from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

    t2t_m = "facebook/m2m100_418M"
    t2t_pipe = pipeline(task='text2text-generation', model=t2t_m)

    model = M2M100ForConditionalGeneration.from_pretrained(t2t_m)
    tokenizer = M2M100Tokenizer.from_pretrained(t2t_m)

    nlp_stanza = stanza.Pipeline(lang="multilingual", processors="langid",
                                 download_method=DownloadMethod.REUSE_RESOURCES)
    text_en_l = []
    for text in texts:
        if text == "":
            text_en_l = text_en_l + [text]
            continue

        doc = nlp_stanza(text)
        #print(doc.lang)
        if doc.lang == "en":
            text_en_l = text_en_l + [text]
            # print(text)
        else:
            # convert to model supported language code
            # https://stanfordnlp.github.io/stanza/available_models.html
            # https://github.com/huggingface/transformers/blob/main/src/transformers/models/m2m_100/tokenization_m2m_100.py
            lang = doc.lang
            if lang == "fro":  # fro = Old French
                lang = "fr"
            elif lang == "la":  # latin
                lang = "it"
            elif lang == "nn":  # Norwegian (Nynorsk)
                lang = "no"
            elif lang == "kmr":  # Kurmanji
                lang = "tr"

            case = 2

            if case == 1:
                text_en = t2t_pipe(text, forced_bos_token_id=t2t_pipe.tokenizer.get_lang_id(lang='en'))
                text_en = text_en[0]['generated_text']
            elif case == 2:
                tokenizer.src_lang = lang
                encoded_hi = tokenizer(text, return_tensors="pt")
                generated_tokens = model.generate(**encoded_hi, forced_bos_token_id=tokenizer.get_lang_id("en"))
                text_en = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
                text_en = text_en[0]
            else:
                text_en = text
            text_en_l = text_en_l + [text_en]
            #print(text)
            #print(text_en)
    return text_en_l