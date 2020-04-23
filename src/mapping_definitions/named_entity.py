import typing

from src.container import TripletContainer
from src.external.phrase_normalizer import PhaseNormalizerCategory
from src.words.named_entity import INamedEntitiesWord


def __format_chunk_to_name(pipe, chunk: typing.List[INamedEntitiesWord], action: PhaseNormalizerCategory):
    name = " ".join(x.form for x in chunk if not x.is_punct)

    if pipe.phrase_normalizer is not None:
        name = pipe.phrase_normalizer.normalize(action, name)

    return f"\"{name}\""


def person_chunk_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord], container: TripletContainer,
                        default_mapping: str):
    container.update_instance_value(root_id, 'person')
    name_id = container.get_generated_id()
    container.add_instance(root_id, name_id, 'name', 'name')

    for i in range(len(chunk)):
        container.add(name_id, f"op{i}", f"\"{chunk[i].lemma}\"")


def concat_chunk_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord], container: TripletContainer,
                        default_mapping: str, action: PhaseNormalizerCategory = PhaseNormalizerCategory.NONE):
    container.update_instance_value(root_id, default_mapping)
    name_id = container.get_generated_id()
    container.add_instance(root_id, name_id, "name", "name")

    name = __format_chunk_to_name(pipe, chunk, action)
    container.add(name_id, f"op1", name)


def concat_chunk_location_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord],
                                 container: TripletContainer,
                                 default_mapping: str):
    container.update_instance_value(root_id, "name")
    name = __format_chunk_to_name(pipe, chunk, PhaseNormalizerCategory.LOCATION)
    container.add_instance(root_id, container.get_generated_id(), "op1", name)
    container.replace_instance_left_roles(root_id, "mod", "location")


def concat_chunk_organization_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord],
                                     container: TripletContainer,
                                     default_mapping: str):
    concat_chunk_action(pipe, root_id, chunk, container, default_mapping, PhaseNormalizerCategory.ORGANIZATION)


def concat_chunk_general_normalized_action(pipe, root_id: str, chunk: typing.List[INamedEntitiesWord],
                                           container: TripletContainer,
                                           default_mapping: str):
    concat_chunk_action(pipe, root_id, chunk, container, default_mapping, PhaseNormalizerCategory.NOCATEGORY)

