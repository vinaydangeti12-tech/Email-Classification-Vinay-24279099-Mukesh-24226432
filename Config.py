class Config:
    # Directories and Paths
    DATA_DIR = 'data/'
    APPGALLERY_PATH = 'data/AppGallery.csv'
    PURCHASING_PATH = 'data/Purchasing.csv'

    # Input Columns
    TICKET_SUMMARY = 'Ticket Summary'
    INTERACTION_CONTENT = 'Interaction content'

    # Type Columns
    TYPE1 = 'y1'
    TYPE2 = 'y2'
    TYPE3 = 'y3'
    TYPE4 = 'y4'
    TYPE_COLS = ['y2', 'y3', 'y4']
    GROUPED = 'y1'

    # Modeling constraints
    MIN_CLASS_COUNT = 3
    MIN_TEST_SAMPLES = 1
    RANDOM_STATE = 0
    CHAIN_SEP = " | "


