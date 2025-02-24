"""
Merge configurations are YAML documents specifying the operations to perform in order to produce your merged model. 
Below are the primary elements of a configuration file:
    `merge_method`: Specifies the method to use for merging models. See Merge Methods for a list.
    
    `slices`: Defines slices of layers from different models to be used. 
            This field is mutually exclusive with models.
    
    `models`: Defines entire models to be used for merging. 
            This field is mutually exclusive with slices.
    
    `base_model`: Specifies the base model used in some merging methods.
    
    `parameters`: Holds various parameters such as weights and densities, 
                which can also be specified at different levels of the configuration.
    
    `dtype`: Specifies the data type used for the merging operation.
    
    `tokenizer` or `tokenizer_source`: Determines how to construct a tokenizer for the merged model.
    
    `chat_template`: Specifies a chat template for the merged model.
""".strip()

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, Union, List
import yaml
from pathlib import Path


@dataclass
class MergeConfig:
    merge_method: str = None
    dtype: str = None
    slices: Optional[List[Dict[str, Any]]] = None
    models: Optional[List[Dict[str, Any]]] = None
    base_model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = field(default_factory=dict)
    tokenizer: Optional[Union[str, Dict[str, Any]]] = None
    tokenizer_source: Optional[str] = None
    chat_template: Optional[str] = None

    def update(self, **kwargs):
        """Update configuration attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid attribute: {key}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary, excluding None values."""
        config_dict = asdict(self)
        return {k: v for k, v in config_dict.items() if v is not None}

    def to_yaml(self, file_path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        file_path = Path(file_path)
        config_dict = self.to_dict()

        with file_path.open("w") as f:
            yaml.safe_dump(config_dict, f, sort_keys=False)

    @classmethod
    def from_yaml(cls, file_path: Union[str, Path]) -> "MergeConfig":
        """Load configuration from YAML file."""
        file_path = Path(file_path)

        with file_path.open("r") as f:
            config_dict = yaml.safe_load(f)

        return cls(**config_dict)
