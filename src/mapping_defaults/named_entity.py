import typing
from abc import ABC, abstractmethod

from src.delegates import ChunkDelegate
from src.mapping_definitions.named_entity import person_chunk_action, concat_chunk_action, \
    concat_chunk_location_action, concat_chunk_organization_action

# The 'allowed' categories, such as person, in AMR can be found here:
# https://github.com/amrisi/amr-guidelines/blob/master/amr.md#named-entities
# For simplicity only general ones are used, such as person and organization
# ToDo: define rest of mapping_definitions
DEFAULT_IOB_ACTION_MAPPING = {
    "person": ChunkDelegate(person_chunk_action),
    "organization": ChunkDelegate(concat_chunk_organization_action, "organization"),
    # This should modify :mod to :location instead? What about detailing the location, for ex., state, city, etc. Has place for improvement
    "location": ChunkDelegate(concat_chunk_location_action, "location"),
    #"event": ChunkDelegate(concat_chunk_action, "event"),
    #"product": ChunkDelegate(concat_chunk_action, "product"),
    #"GPE": ChunkDelegate(concat_chunk_action, "country"),
}


class INamedEntitiesMapping(ABC):

    @abstractmethod
    def get_iob_action_mapping(self):
        pass


class NamedEntitiesMapping:
    """This class contains mapping_definitions and actions which propbank uses to transform PropBank to AMR"""

    def __init__(self, iob_action_mapping: typing.Dict[str, ChunkDelegate] = None):
        self.iob_action_mapping = \
            iob_action_mapping if iob_action_mapping is not None else DEFAULT_IOB_ACTION_MAPPING

    def get_iob_action_mapping(self):
        return self.iob_action_mapping