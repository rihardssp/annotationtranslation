import configparser


class PropBankPipeConfigReader:
    """This class defines PropBankPipe configuration interface"""

    def get_frame_folder(self):
        pass

    def get_propbank_conllu_file_path(self):
        pass


class UniversalDependencyPipeConfigReader:
    """This class defines PropBankPipe configuration interface"""

    def get_ud_conllu_file_path(self):
        pass


class ConfigReader(PropBankPipeConfigReader, UniversalDependencyPipeConfigReader):
    """This class provides config reading functionality"""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('../config.ini')

    def get_root_path(self):
        return "../"

    def get_value(self, section, key):
        return self.config.get(section, key)

    def get_propbankpipe_value(self, key):
        return self.get_value('PropBankPipe', key)

    def get_frame_folder(self):
        return self.get_root_path() + self.get_propbankpipe_value('FrameFolder')

    def get_propbank_conllu_file_path(self):
        return self.get_root_path() + self.get_propbankpipe_value('ConlluFile')

    def get_default_value(self, key):
        return self.get_value('Default', key)

    def get_output_file_path(self):
        return self.get_root_path() + self.get_default_value('OutputFile')
