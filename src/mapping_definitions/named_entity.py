import typing

from src.container import TripletContainer
from src.external.phrase_normalizer import PhaseNormalizerCategory
from src.words.named_entity import INamedEntitiesWord


def __format_chunk_to_name(pipe, chunk: typing.List[INamedEntitiesWord], action: PhaseNormalizerCategory):
    """Formats chunk into a single name and normalised is used if its defined"""
    name = " ".join(x.form for x in chunk if not x.is_punct)

    if pipe.phrase_normalizer is not None:
        name = pipe.phrase_normalizer.normalize(action, name)

    return f"\"{name}\""


def person_chunk_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord], container: TripletContainer,
                        default_mapping: str):
    """Defines person with name"""
    container.update_instance_value(root_id, 'person')
    name_id = container.get_generated_id()
    container.add_instance(root_id, name_id, 'name', 'name')

    for i in range(len(chunk)):
        container.add(name_id, f"op{i}", f"\"{chunk[i].lemma}\"")


def string_concat_chunk_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord], container: TripletContainer,
                                           default_mapping: str):
    """Joins the chunk and just updates the element that chunk came from"""
    name = __format_chunk_to_name(pipe, chunk, PhaseNormalizerCategory.NOCATEGORY)
    container.update_instance_value(root_id, name)


def instance_with_name_concat_chunk_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord], container: TripletContainer,
                                           default_mapping: str, action: PhaseNormalizerCategory = PhaseNormalizerCategory.NONE):
    """Create an object with default mapping and adds chunk as name"""
    container.update_instance_value(root_id, default_mapping)
    name_id = container.get_generated_id()
    container.add_instance(root_id, name_id, "name", "name")

    name = __format_chunk_to_name(pipe, chunk, action)
    container.add(name_id, f"op1", name)


def concat_chunk_organization_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord],
                                     container: TripletContainer,
                                     default_mapping: str):
    instance_with_name_concat_chunk_action(pipe, root_id, chunk, container, default_mapping, PhaseNormalizerCategory.ORGANIZATION)


def instance_with_name_concat_normalised_chunk_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord],
                                                      container: TripletContainer,
                                                      default_mapping: str):
    instance_with_name_concat_chunk_action(pipe, root_id, chunk, container, default_mapping, PhaseNormalizerCategory.NOCATEGORY)


def concat_chunk_location_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord],
                                 container: TripletContainer,
                                 default_mapping: str):
    """Concatinates chunk into a property :location (if its not :mod it stays with existing role)"""

    # ToDo: location categories (city, country, etc)?
    container.update_instance_value(root_id, "name")
    name = __format_chunk_to_name(pipe, chunk, PhaseNormalizerCategory.LOCATION)
    container.add_instance(root_id, container.get_generated_id(), "op1", name)
    container.replace_instance_left_roles(root_id, "mod", "location")


def concat_chunk_time_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord],
                                           container: TripletContainer,
                                           default_mapping: str):
    """Chunk action for time. Propbank time words (ids) are not merged as they're not instances with a separate id
    (or generated in some cases)"""
    root_value = container.get_instance_value(root_id)

    # Avoid over-writing existing time structures
    # ToDo: should actually verify that these structures are filled with all data
    if root_value not in ["date-entity", "temporal-quantity"]:
        # ToDo: convert to proper object
        name = __format_chunk_to_name(pipe, chunk, PhaseNormalizerCategory.NOCATEGORY)
        container.update_instance_value(root_id, name)
