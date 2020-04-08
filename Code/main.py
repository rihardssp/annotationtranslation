import typing
import codecs
import time
from Code.Configuration import ConfigReader
from Code.Container import TripletContainer
from Code.Mappings import PropbankMappings
from Code.Pipe import PropBankPipe
import i18n
i18n.load_path.append('../Translations')
i18n.set('locale', 'lv')
i18n.set('fallback', 'en')
print(i18n.t('foo.foo'))

# Define the pipeline
config_reader = ConfigReader()
pipe_line = [
    PropBankPipe(config_reader, PropbankMappings())
]

before_calc = time.perf_counter()

# The magic
triplet_list: typing.List[TripletContainer] = []
for p in pipe_line:
    triplet_list = p.process_amr(triplet_list)

after_calc = time.perf_counter()
print(f"Calculation ran {after_calc - before_calc:0.4f} seconds")

# Store in file
f = codecs.open(config_reader.get_output_file_path(), "w", "utf-8")
for triplet in triplet_list:
    triplet.print(f)
f.close()
