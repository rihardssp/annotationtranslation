import configparser

class PropBankPipeConfigReader:
    """This class defines PropBankPipe configuration interface"""

    def get_frame_folder(self):
        pass

    def get_conllu_file(self):
        pass

class ConfigReader(PropBankPipeConfigReader):
    """This class provides config reading functionality"""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def get_value(self, section, key):
         return self.config.get(section, key)

    def get_PropBankPipe_value(self, key):
         return self.get_value('PropBankPipe', key)

    def get_frame_folder(self):
        return self.get_PropBankPipe_value('FrameFolder')

    def get_conllu_file(self):
        return self.get_PropBankPipe_value('ConlluFile')


