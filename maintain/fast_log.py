import logging
import logging.config
import sys

def set_log(path=None,level='DEBUG'):
    if path:
        config = {
            'version': 1,
            'formatters': {
                'standard': {
                    #'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    #'format': '%(levelname)s %(asctime)s %(message)s',
                    'format': '%(levelname)s %(asctime)s %(process)d-%(thread)d %(message)s'
                },
                # 其他的 formatter
            },
            'handlers': {
                'console': {
                    'level':'DEBUG',
                    'class': 'logging.StreamHandler',
                    'stream': sys.stdout
                    }, 
                'rotfile':{
                    #'level': 'DEBUG',
                    #'class': 'logging.handlers.RotatingFileHandler',
                     ##'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
                    #'maxBytes': 1024*1024*5,
                    #'backupCount':3,
                    #'formatter':'standard',
                    #'filename': path, 
                    'level': 'DEBUG',
                    'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
                    'maxBytes': 1024*1024*5,
                    'backupCount':3,
                    'formatter':'standard',
                    'filename': path,    
                    'encoding': 'utf8',                    
                },  
            },
            'loggers':{
                '':{
                    'handlers': ['rotfile' ], # 'console',
                    'level': level,
                    'propagate': True,  
                },
                'general_log':{
                    #'propagate': True,  
                }
                
                # 其他的 Logger
            }
        }
    else:
        config = {
          'version': 1,
          'formatters': {
              'standard': {
                  #'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                  #'format': '%(levelname)s %(asctime)s %(message)s',
                  'format': '%(levelname)s %(asctime)s %(process)d-%(thread)d %(message)s'
              },
              # 其他的 formatter
          },
          'handlers': {
              'console': {
                  'level':'DEBUG',
                  'class': 'logging.StreamHandler',
                  'stream': sys.stdout
                  }, 
          },
          'loggers':{
              '':{
                  'handlers': ['console' ],
                  'level': level,
                  'propagate': True,  
              },
              'general_log':{
                  'propagate': True,  
              }
              
              # 其他的 Logger
          }
      }
  
    logging.config.dictConfig(config)
