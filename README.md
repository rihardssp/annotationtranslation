# Annotation Translation is a tool that uses UD, PropBank, Named Entities, CoReferences to create AMR graphs.

The goal is to make manual annotation easier by having a backbone AMR generated from already annotated material.

## The source code structure:

- **src:** code
  - **caches:** contains cache implementations.
  - **container:** class responsible for manipulating and printing AMR.
  - **external:** External services.
  - **mapping_defaults:** default mapping for pipes. For example PropBank role -> AMR role or logic.
  - **mapping_definitions:** defines logic to be used in mapping_defaults
  - **pipes:** a part of the pipeline for creating AMR - takes AMR list as input, with the only exception being PropBank pipe, which creates a list instead.
  - **readers:** logic to get annotation text into sentences/words.
  - **sentences:** logic that is used by pipe to query words.
  - **words:** defines given annotation properties.

Separate modules:
- **delegates:** define how mapping logic is handled.
- **localisation:** i18n helper
- **configuration:** reads input from config.ini

Naming convention is as follows: if its pipe specific then class/module name must show it.


## ResultExamples

There are multiple examples of AnnotationTranslation results.
Latvian language examples were generated from https://github.com/LUMII-AILab/FullStack by using UD, PropBank, CoReferences, Named Entities.
Other examples were generated from respective sources (at the start of the file) with only PropBank as input.

If an example has statistics with it: its a file showing the coverage of annotations for AMR graph set and also how
much of information was obtained from each annotation.

## AmrHandAnnotated.txt

The gold standard for Latvian language.
HandAnnotatedInput.conllu - PropBank file used to generate all AMR graphs within Latvian gold standard for comparison.
Its a subset of PropBank available in https://github.com/LUMII-AILab/FullStack. For quality analysis Named Entities and CoReferences were also used.


# Setup

requirements.txt defines all packages necessary to run the translator.
config.ini file contains variable values used within different modules of project, for example, input file location.

To get started you can try using inputs from https://github.com/LUMII-AILab/FullStack
and put them into the following folders (PropBank is the deciding factor in how many graphs there are, additional CoReference or Named Entities are ignored):

[PropBankPipe]
ResourceFile = ..\Resources\lv-up-all.conllu
[CoReferencePipe]
ResourceFolder = ..\Resources\CoReferences\
[NamedEntitiesPipe]
ResourceFolder = ..\Resources\NamedEntities\


# main.py

Currently the only way to configure specific pipes/readers.
To change used pipes:
# Define the pipeline and readers you must edit the following (pipes constructor might give some hints):

pipe_line = [
    PropBankPipe(PropBankMapping()),
    NamedEntitiesPipe(NamedEntitiesMapping(), phrase_normalizer=RestletPhraseNormalizer()),
    CoReferencePipe()
]

The rest of the code is statistics/i18n.
