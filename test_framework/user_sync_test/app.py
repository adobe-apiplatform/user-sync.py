import logging

def main():
    try:
        print('test')
    except:
        logger.error('TEST')
        
logger = logging.getLogger('main')

if __name__ == '__main__':
    main()