import os

os.environ['FLAGS_enable_onednn'] = '0'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from app import main

if __name__ == "__main__":
    main()