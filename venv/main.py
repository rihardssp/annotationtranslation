import typing
import codecs
from Container import *
from Pipe import *
from Configuration import *

# Define the pipeline
config_reader = ConfigReader()
pipe_line = [
    PropBankPipe(config_reader),
    UniversalDependencyPipe(config_reader)
]

# The magic
triplet_list: typing.List[TripletContainer] = []
for p in pipe_line:
    triplet_list = p.process_amr(triplet_list)

# Store in file
f = codecs.open(config_reader.get_output_file_path(), "w", "utf-8")
for triplet in triplet_list:
    triplet.print(f)
f.close()
