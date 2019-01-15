# Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`namespace `[`doc_converter::app::common::util`](#namespacedoc__converter_1_1app_1_1common_1_1util) | 
`namespace `[`doc_converter::app::converter`](#namespacedoc__converter_1_1app_1_1converter) | 
`namespace `[`doc_converter::app::models::invalid_usage`](#namespacedoc__converter_1_1app_1_1models_1_1invalid__usage) | 
`namespace `[`doc_converter::app::processmgr::processmgr`](#namespacedoc__converter_1_1app_1_1processmgr_1_1processmgr) | 

# namespace `doc_converter::app::common::util` 

## Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`public def `[`handle_exception`](#util_8py_1a846915d744d45a8346638c70ca4453fe)`(exc_type,exc_value,exc_traceback)`            | Catches unhandled exceiptions for logger.

## Members

#### `public def `[`handle_exception`](#util_8py_1a846915d744d45a8346638c70ca4453fe)`(exc_type,exc_value,exc_traceback)` 

Catches unhandled exceiptions for logger.

# namespace `doc_converter::app::converter` 

## Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`public def `[`handle_invalid_usage`](#converter_8py_1a3abedc035189ab57d83cadc696f79c33)`(error)`            | Handles invalid_usage errors.
`public def `[`hello`](#converter_8py_1a57db9aca43562859b23a8f3100166516)`()`            | test function
`public def `[`invalid_file`](#converter_8py_1a47c581465f1f4015444a9c7ad0642736)`()`            | Exception for invalid file extensions.
`public def `[`bad_request`](#converter_8py_1a667f04d4b515262f1b8cacb468f18dac)`()`            | extension for catch all api errors based on client input
`public def `[`server_error`](#converter_8py_1a7b73ab761a8a77796924e0b6b93b6697)`()`            | Exception catch all for client errors based on server problems.
`public def `[`svgconvert`](#converter_8py_1acfed3f9337657677941282b1c7921be6)`()`            | 

## Members

#### `public def `[`handle_invalid_usage`](#converter_8py_1a3abedc035189ab57d83cadc696f79c33)`(error)` 

Handles invalid_usage errors.

#### `public def `[`hello`](#converter_8py_1a57db9aca43562859b23a8f3100166516)`()` 

test function

#### `public def `[`invalid_file`](#converter_8py_1a47c581465f1f4015444a9c7ad0642736)`()` 

Exception for invalid file extensions.

#### `public def `[`bad_request`](#converter_8py_1a667f04d4b515262f1b8cacb468f18dac)`()` 

extension for catch all api errors based on client input

#### `public def `[`server_error`](#converter_8py_1a7b73ab761a8a77796924e0b6b93b6697)`()` 

Exception catch all for client errors based on server problems.

#### `public def `[`svgconvert`](#converter_8py_1acfed3f9337657677941282b1c7921be6)`()` 

# namespace `doc_converter::app::models::invalid_usage` 

## Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`class `[`doc_converter::app::models::invalid_usage::invalid_usage`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage) | Holds classes for error messages.

# class `doc_converter::app::models::invalid_usage::invalid_usage` 

```
class doc_converter::app::models::invalid_usage::invalid_usage
  : public Exception
```  

Holds classes for error messages.

returns a custom error message to client

## Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`public  `[`message`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage_1ae2cbd35368a9c600911a47b59ef3f1b9) | 
`public  `[`status_code`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage_1a8ed1a9b3d4a77d7759ffaeeec9bb0ef5) | 
`public  `[`payload`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage_1a09fea03223675ecb9e18ec87bbbba13c) | 
`public def `[`__init__`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage_1a47db354a73691a9c45b341a9c8d68648)`(self,message,status_code,payload)` | 
`public def `[`to_dict`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage_1a8f1d497c9075c93b928ed9e13d867262)`(self)` | converts message to dictionary for conversion into json payload

## Members

#### `public  `[`message`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage_1ae2cbd35368a9c600911a47b59ef3f1b9) 

#### `public  `[`status_code`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage_1a8ed1a9b3d4a77d7759ffaeeec9bb0ef5) 

#### `public  `[`payload`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage_1a09fea03223675ecb9e18ec87bbbba13c) 

#### `public def `[`__init__`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage_1a47db354a73691a9c45b341a9c8d68648)`(self,message,status_code,payload)` 

#### `public def `[`to_dict`](#classdoc__converter_1_1app_1_1models_1_1invalid__usage_1_1invalid__usage_1a8f1d497c9075c93b928ed9e13d867262)`(self)` 

converts message to dictionary for conversion into json payload

# namespace `doc_converter::app::processmgr::processmgr` 

## Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`class `[`doc_converter::app::processmgr::processmgr::processmgr`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr) | Container class for managing interface between flask and libreoffice subprocesses.

# class `doc_converter::app::processmgr::processmgr::processmgr` 

Container class for managing interface between flask and libreoffice subprocesses.

## Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`public  `[`in_filepath`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1ad4f5facdb9cc73aea1e018de39f0dac6) | 
`public  `[`convert_type`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a027e310cd2cad579b2cfcf5db557495d) | 
`public  `[`file_extension`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a47e324623c5d622f7b75a74ef96d457a) | 
`public  `[`out_dir`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a5c2c0d252887948fec25416759c87926) | 
`public  `[`converted`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a8d7494573775cb9f0e4498782e123551) | 
`public  `[`outfile`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a83de30ba5eb9507e802f89686ae1e462) | 
`public  `[`command`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a082a6aec3774ea258ce4a93ee56ae6d7) | 
`public  `[`filter`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a273ae5986b8b374d31016f11d7b0a91b) | 
`public def `[`__init__`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a4c1863826806ca32bf53c65e986bc1d1)`(self,in_filepath,convert_type,out_dir)` | 
`public def `[`build_filter`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a8405875f7e2d49b98ff92157d0af9b62)`(self)` | builds the libreoffice 'filter' for commmand line file conversion
`public def `[`build_command`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1af1a013bb4118244289136f16f6bd0065)`(self)` | 
`public def `[`check_command`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1abefa9394fac5378095f11134167bf610)`(self)` | 
`public def `[`convert`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1af2fed45e35343a2acf3d89036b2a4051)`(self)` | Converts a file using the libreoffice command line interface.

## Members

#### `public  `[`in_filepath`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1ad4f5facdb9cc73aea1e018de39f0dac6) 

#### `public  `[`convert_type`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a027e310cd2cad579b2cfcf5db557495d) 

#### `public  `[`file_extension`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a47e324623c5d622f7b75a74ef96d457a) 

#### `public  `[`out_dir`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a5c2c0d252887948fec25416759c87926) 

#### `public  `[`converted`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a8d7494573775cb9f0e4498782e123551) 

#### `public  `[`outfile`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a83de30ba5eb9507e802f89686ae1e462) 

#### `public  `[`command`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a082a6aec3774ea258ce4a93ee56ae6d7) 

#### `public  `[`filter`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a273ae5986b8b374d31016f11d7b0a91b) 

#### `public def `[`__init__`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a4c1863826806ca32bf53c65e986bc1d1)`(self,in_filepath,convert_type,out_dir)` 

#### `public def `[`build_filter`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1a8405875f7e2d49b98ff92157d0af9b62)`(self)` 

builds the libreoffice 'filter' for commmand line file conversion

#### `public def `[`build_command`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1af1a013bb4118244289136f16f6bd0065)`(self)` 

#### `public def `[`check_command`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1abefa9394fac5378095f11134167bf610)`(self)` 

#### `public def `[`convert`](#classdoc__converter_1_1app_1_1processmgr_1_1processmgr_1_1processmgr_1af2fed45e35343a2acf3d89036b2a4051)`(self)` 

Converts a file using the libreoffice command line interface.

The converted filename is output.

Generated by [Moxygen](https://sourcey.com/moxygen)