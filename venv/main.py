import typing
import codecs
from Container import *
from Pipe import *
from Configuration import *

# Define the pipeline
pipe_line = [
    PropBankPipe(ConfigReader())
]

# The magic
triplet_list: typing.List[TripletContainer] = []
for p in pipe_line:
    triplet_list = p.process_amr(triplet_list)

# Store in file
f = codecs.open("output.txt", "w", "utf-8")
for triplet in triplet_list:
    triplet.print(f)
f.close()
