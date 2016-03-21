# Libraries used in IoTQATools

## **cb_v2_utils.py**
 Manage Context broker operations
 - **constructor**: define protocol, host, and port used in requests. Initialize all context dict (headers, entity, parameters, subscription)

#### Operations:
##### Generals:
 - **get_version_request**: return the Context Broker version installed
 - **get_statistics_request**: return the Context Broker statistics
 - **get_cache_statistics_request**: return the Context Broker cache statistics
 - **get_base_request**: offers the initial API affordances in the form of the links in the JSON body
 - **harakiri**: Orion context broker exits in an ordered manner
      hint: the -harakiri option is used to kill contextBroker (must be compiled in DEBUG mode)
 - **is_cb_started**: determine whether cb is started or not
 - **definition_headers**: definition of headers using a table of data.
```
| parameter          | value            |
| Fiware-Service     | happy_path       |
```
 - **modification_headers**: modification or append of headers and determine if the previous headers are kept or not ( true | false )
```
| parameter          | value            |
| Content-Type       | application/json |
```

##### Entity:
- **properties_to_entities**: definition of properties to entities
```
| parameter      | value   |
| entities_type  | house   |
```
- **create_entities**: create N entities in modes diferents (POST /v2/entities/). the prefixes use a table of data.
```
| entity | prefix |
| id     | true   |
```
mode: define in that format will be created the entity (normalized | keyValues | values), it is not the query parameter (options), else the mode to generate the request.

normalized:
 ```
   "attr": {
        "value": "45",
        ...
   }
```
keyValues:
```
   "attr": "45"
```
Hints:
    - If entity id prefix is true, the entity id is value plus a suffix (consecutive), ex:
         `entity_id=room_0, entity_id=room_1, ..., entity_id=room_N`
    - If entity type prefix is true, the entity type is value plus a suffix (consecutive), ex:
         `entity_type=room_0, entity_type=room_1, ..., entity_type=room_N`
    - The prefixes function (id or type) are used if entities_number is greater than 1.
- **create_entity_raw**: create an entity with an attribute and raw values (compound, vector, boolean, integer, etc) in differents modes. It is similar to "create_entities" operation.
- **list_all_entities**: list all entities (GET /v2/entities/). Queries parameters use a tabla of data.
```
| parameter | value                 |
| limit     | 2                     |
| offset    | 3                     |
```
- **list_an_entity_by_id**: get an entity by ID (GET v2/entities/<entity_id>). Queries parameters use a tabla of data.
```
| parameter | value       |
| attrs     | temperature |
```
   Hint: if we need " char, use \' and it will be replaced (mappping_quotes)
- **list_an_attribute_by_id**: get an attribute or an attribute value by ID. Queries parameters use a tabla of data.
```
   - GET v2/entities/<entity_id>/attrs/<attribute_name>/
   - GET v2/entities/<entity_id>/attrs/<attribute_name>/value
```   
- **get_entity_types**: get entity types (GET /v2/types). Queries parameters use a tabla of data.
- **update_or_append_an_attribute_by_id**: update or append an attribute by id (POST, PATCH, PUT /v2/entities/<entity_id>). Queries parameters use a tabla of data.
mode in that will be created attributes in request ( normalized | keyValues | values)
Hint: if would like a query parameter name, use `qp_` prefix
- **update_or_append_an_attribute_in_raw_by_id**: update or append an entity with raw value per special cases (compound, vector, boolean, integer, etc). It is similar to "update_or_append_an_attribute_by_id" operation.
- **update_an_attribute_by_id_and_by_name**: update an attribute or an attribute value by ID and attribute name if it exists. Queries parameters use a tabla of data.
```
   - PUT /v2/entities/<entity_id>/attrs/<attr_name>
   - PUT /v2/entities/<entity_id>/attrs/<attr_name>/value
```   
   Hint: if would like a query parameter name, use `qp_` prefix
- **update_an_attribute_by_id_and_by_name_in_raw_mode**: update an attribute by ID and attribute name if it exists in raw mode. It is similar to "update_an_attribute_by_id_and_by_name" operation.
- **delete_entities_by_id**: delete entities or attribute. Queries parameters use a tabla of data.
```
   - DELETE  /v2/entities/<entity_id>
   - DELETE  /v2/entities/<entity_id>/attrs/<attr_name>
```   

##### Get used values per the library
- **get_entity_context**: return entities contexts (dict)
- **get_headers**: return headers (dict)
- **get_entities_parameters**: return queries parameters (dict)
- **get_entities_prefix**: return if entity id or entity type are used as prefix (dict)
- **get_entity_id_to_request**: return entity id used in request to get an entity, used to verify if the entity returned is the expected (string)
- **get_entity_type_to_request**: return entity type used in request to get/delete an entity, used to verify if the entity returned is the expected (string)
- **get_attribute_name_to_request**: return attribute name used in request to get an attribute, used to verify if the attribute returned is the expected (string)
