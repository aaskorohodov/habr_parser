import time

from parser_app.controllers.main_controller import MainController
from parser_app.logger.standard_logger import STDLogger
from parser_app.utils.constants import PARSER_DB_CHECK_INTERVAL, ENV_FILE_PATH
from parser_app.utils.env_setter import EnvSetter


if __name__ == '__main__':
    while True:
        try:
            EnvSetter.set_envs(ENV_FILE_PATH)
            logger = STDLogger
            main_controller = MainController(PARSER_DB_CHECK_INTERVAL, logger)
            main_controller.start()
        except Exception as e:
            print(f'An error occurred, during running parser-application:'
                  f'\n\n'
                  f'{e.__str__()}'
                  f'\n\n'
                  f'Restarting in 10 seconds...')
            time.sleep(10)
