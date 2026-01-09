"""
Settings management module for SHARP 3DGS Generator.
Copyright 2025 ANDRII SHRAMKO

Manages all quality settings and configuration for SHARP model.
"""

import json
from pathlib import Path
from typing import Dict, Any


class SharpSettings:
    """Manages all SHARP model settings."""
    
    def __init__(self, settings_file: Path = None):
        """Initialize settings with defaults."""
        if settings_file is None:
            settings_file = Path(__file__).parent / "settings.json"
        self.settings_file = settings_file
        
        # Default settings - all SHARP parameters
        # IMPORTANT: Architecture parameters (stride, steps, base_width) must match checkpoint!
        # Only non-architecture parameters can be safely optimized
        self.defaults = {
            # Device settings
            "device": "default",  # default, cuda, cpu, mps
            
            # Path settings (for video app)
            "last_video_path": None,  # Last selected video file path
            "last_output_dir": None,  # Last selected output directory
            
            # Initializer parameters - MUST MATCH CHECKPOINT ARCHITECTURE
            "initializer_stride": 2,  # Default from SHARP (changing breaks checkpoint compatibility)
            "initializer_num_layers": 2,  # Must be 2 when num_monodepth_layers > 1 (SHARP requirement)
            "initializer_scale_factor": 1.0,  # Can be optimized (affects Gaussian size)
            "initializer_disparity_factor": 1.0,  # Can be optimized (affects depth estimation)
            "initializer_color_option": "all_layers",  # none, first_layer, all_layers
            "initializer_first_layer_depth_option": "surface_min",  # surface_min, surface_max, base_depth, linear_disparity
            "initializer_rest_layer_depth_option": "surface_min",
            "initializer_base_depth": 10.0,
            "initializer_normalize_depth": True,
            "initializer_feature_input_stop_grad": False,
            "initializer_output_inpainted_layer_only": False,
            "initializer_set_uninpainted_opacity_to_zero": False,
            "initializer_concat_inpainting_mask": False,
            
            # Gaussian decoder parameters - MUST MATCH CHECKPOINT ARCHITECTURE
            "gaussian_decoder_stride": 2,  # Default from SHARP (changing breaks checkpoint compatibility)
            "gaussian_decoder_norm_type": "group_norm",  # group_norm, etc.
            "gaussian_decoder_norm_num_groups": 8,
            "gaussian_decoder_use_depth_input": True,
            "gaussian_decoder_image_encoder_type": "skip_conv_kernel2",  # skip_conv, skip_conv_kernel2
            "gaussian_decoder_grad_checkpointing": False,
            "gaussian_decoder_upsampling_mode": "transposed_conv",
            
            # Main predictor parameters
            "max_scale": 10.0,
            "min_scale": 0.0,
            "color_space": "linearRGB",  # linearRGB, sRGB
            "norm_type": "group_norm",
            "norm_num_groups": 8,
            "use_predicted_mean": False,
            "color_activation_type": "sigmoid",  # sigmoid, exp, etc.
            "opacity_activation_type": "sigmoid",
            "low_pass_filter_eps": 0.001,  # Lower = less smoothing, more detail (optimized for maximum detail)
            
            # Processing resolution - CAN BE OPTIMIZED FOR QUALITY
            # IMPORTANT: Model uses patch-based encoding with patch_size=384
            # Resolution must be compatible with patch splitting algorithm
            # Safe values: 1536 (default), 1920, 2304, 3072, 3840, 4608, 6144
            # Maximum tested: ~6144 (requires 16GB+ VRAM)
            # Values must be multiples of 384 or compatible with patch stride calculations
            "processing_resolution": 1536,  # Range: 512-6144 (must be compatible with 384-patch encoding)
            "num_monodepth_layers": 2,  # Keep at 2 (3 may not be supported)
            "sorting_monodepth": False,
            "base_scale_on_predicted_mean": True,
            
            # Delta factors (learning rate multipliers)
            "delta_factor_xy": 0.001,
            "delta_factor_z": 0.001,
            "delta_factor_color": 0.1,
            "delta_factor_opacity": 1.0,
            "delta_factor_scale": 1.0,
            "delta_factor_quaternion": 1.0,
            
            # Alignment parameters - MUST MATCH CHECKPOINT ARCHITECTURE
            "alignment_kernel_size": 16,
            "alignment_stride": 1,
            "alignment_frozen": False,
            "alignment_steps": 4,  # Default from SHARP (changing breaks checkpoint compatibility)
            "alignment_activation_type": "exp",
            "alignment_depth_decoder_features": False,
            "alignment_base_width": 16,  # Default from SHARP (changing breaks checkpoint compatibility)
            
            # Monodepth parameters
            "monodepth_patch_encoder_preset": "dinov2l16_384",
            "monodepth_image_encoder_preset": "dinov2l16_384",
            "monodepth_unfreeze_patch_encoder": False,
            "monodepth_unfreeze_image_encoder": False,
            "monodepth_unfreeze_decoder": False,
            "monodepth_unfreeze_head": False,
            "monodepth_unfreeze_norm_layers": False,
            "monodepth_grad_checkpointing": False,
            "monodepth_use_patch_overlap": True,
            
            # Monodepth adaptor parameters
            "monodepth_adaptor_encoder_features": True,
            "monodepth_adaptor_decoder_features": False,
            
            # Output settings
            "auto_convert_to_standard": True,
            "output_dir": None,  # None = use default
        }
        
        # QUALITY OPTIMIZATION GUIDE:
        # ============================
        # SAFE TO OPTIMIZE (don't affect model architecture):
        # - processing_resolution: 1536 (default), 1920, 2304, 3072, 3840, 4608, 6144 (max)
        #   IMPORTANT: Model uses 384-patch encoding. Resolution MUST be multiple of 384.
        #   Range: 512-6144. Values are automatically rounded to nearest multiple of 384.
        #   WARNING: Resolutions >3072 require significant VRAM (8GB+ for 3072, 16GB+ for 6144)
        # - low_pass_filter_eps: 0.001 (optimized for maximum detail, was 0.01 default)
        # - initializer_scale_factor: 1.0 (default), 0.8-1.2 range (affects Gaussian size)
        # - max_scale: 10.0 (default), can increase for larger objects
        # - initializer_disparity_factor: 1.0 (default), can adjust for depth estimation
        #
        # DO NOT CHANGE (breaks checkpoint compatibility):
        # - initializer_stride, gaussian_decoder_stride, alignment_steps, alignment_base_width
        
        # Load settings
        self.settings = self.defaults.copy()
        self.load()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set setting value."""
        if key in self.defaults:
            self.settings[key] = value
        else:
            raise ValueError(f"Unknown setting: {key}")
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple settings."""
        for key, value in updates.items():
            if key in self.defaults:
                self.settings[key] = value
            else:
                print(f"Warning: Unknown setting '{key}' ignored")
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = self.defaults.copy()
    
    def save(self) -> bool:
        """Save settings to file."""
        try:
            print(f"  Writing to: {self.settings_file}")
            print(f"  Settings count: {len(self.settings)}")
            
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            # Verify write
            if self.settings_file.exists():
                file_size = self.settings_file.stat().st_size
                print(f"  File written: {file_size} bytes")
                return True
            else:
                print(f"  ERROR: File does not exist after write!")
                return False
        except Exception as e:
            import traceback
            print(f"Error saving settings: {e}")
            traceback.print_exc()
            return False
    
    def load(self) -> bool:
        """Load settings from file."""
        if not self.settings_file.exists():
            return False
        
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            
            # Merge with defaults (keep new parameters, validate types)
            for key, value in loaded.items():
                if key in self.defaults:
                    # Type validation
                    default_type = type(self.defaults[key])
                    if isinstance(value, default_type) or (
                        isinstance(self.defaults[key], float) and isinstance(value, (int, float))
                    ):
                        self.settings[key] = value
                    else:
                        print(f"Warning: Invalid type for '{key}', using default")
                else:
                    print(f"Warning: Unknown setting '{key}' ignored")
            
            return True
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings as dictionary."""
        return self.settings.copy()
    
    def apply_to_predictor_params(self, params):
        """Apply settings to PredictorParams object."""
        from sharp.models.params import PredictorParams
        
        # Initializer parameters
        params.initializer.stride = self.settings["initializer_stride"]
        params.initializer.num_layers = self.settings["initializer_num_layers"]
        params.initializer.scale_factor = self.settings["initializer_scale_factor"]
        params.initializer.disparity_factor = self.settings["initializer_disparity_factor"]
        params.initializer.color_option = self.settings["initializer_color_option"]
        params.initializer.first_layer_depth_option = self.settings["initializer_first_layer_depth_option"]
        params.initializer.rest_layer_depth_option = self.settings["initializer_rest_layer_depth_option"]
        params.initializer.base_depth = self.settings["initializer_base_depth"]
        params.initializer.normalize_depth = self.settings["initializer_normalize_depth"]
        params.initializer.feature_input_stop_grad = self.settings["initializer_feature_input_stop_grad"]
        params.initializer.output_inpainted_layer_only = self.settings["initializer_output_inpainted_layer_only"]
        params.initializer.set_uninpainted_opacity_to_zero = self.settings["initializer_set_uninpainted_opacity_to_zero"]
        params.initializer.concat_inpainting_mask = self.settings["initializer_concat_inpainting_mask"]
        
        # Gaussian decoder parameters
        params.gaussian_decoder.stride = self.settings["gaussian_decoder_stride"]
        params.gaussian_decoder.norm_type = self.settings["gaussian_decoder_norm_type"]
        params.gaussian_decoder.norm_num_groups = self.settings["gaussian_decoder_norm_num_groups"]
        params.gaussian_decoder.use_depth_input = self.settings["gaussian_decoder_use_depth_input"]
        params.gaussian_decoder.image_encoder_type = self.settings["gaussian_decoder_image_encoder_type"]
        params.gaussian_decoder.grad_checkpointing = self.settings["gaussian_decoder_grad_checkpointing"]
        params.gaussian_decoder.upsampling_mode = self.settings["gaussian_decoder_upsampling_mode"]
        
        # Main predictor parameters
        params.max_scale = self.settings["max_scale"]
        params.min_scale = self.settings["min_scale"]
        params.color_space = self.settings["color_space"]
        params.norm_type = self.settings["norm_type"]
        params.norm_num_groups = self.settings["norm_num_groups"]
        params.use_predicted_mean = self.settings["use_predicted_mean"]
        params.color_activation_type = self.settings["color_activation_type"]
        params.opacity_activation_type = self.settings["opacity_activation_type"]
        params.low_pass_filter_eps = self.settings["low_pass_filter_eps"]
        params.num_monodepth_layers = self.settings["num_monodepth_layers"]
        params.sorting_monodepth = self.settings["sorting_monodepth"]
        params.base_scale_on_predicted_mean = self.settings["base_scale_on_predicted_mean"]
        
        # Delta factors
        params.delta_factor.xy = self.settings["delta_factor_xy"]
        params.delta_factor.z = self.settings["delta_factor_z"]
        params.delta_factor.color = self.settings["delta_factor_color"]
        params.delta_factor.opacity = self.settings["delta_factor_opacity"]
        params.delta_factor.scale = self.settings["delta_factor_scale"]
        params.delta_factor.quaternion = self.settings["delta_factor_quaternion"]
        
        # Alignment parameters
        params.depth_alignment.kernel_size = self.settings["alignment_kernel_size"]
        params.depth_alignment.stride = self.settings["alignment_stride"]
        params.depth_alignment.frozen = self.settings["alignment_frozen"]
        params.depth_alignment.steps = self.settings["alignment_steps"]
        params.depth_alignment.activation_type = self.settings["alignment_activation_type"]
        params.depth_alignment.depth_decoder_features = self.settings["alignment_depth_decoder_features"]
        params.depth_alignment.base_width = self.settings["alignment_base_width"]
        
        # Monodepth parameters
        params.monodepth.patch_encoder_preset = self.settings["monodepth_patch_encoder_preset"]
        params.monodepth.image_encoder_preset = self.settings["monodepth_image_encoder_preset"]
        params.monodepth.unfreeze_patch_encoder = self.settings["monodepth_unfreeze_patch_encoder"]
        params.monodepth.unfreeze_image_encoder = self.settings["monodepth_unfreeze_image_encoder"]
        params.monodepth.unfreeze_decoder = self.settings["monodepth_unfreeze_decoder"]
        params.monodepth.unfreeze_head = self.settings["monodepth_unfreeze_head"]
        params.monodepth.unfreeze_norm_layers = self.settings["monodepth_unfreeze_norm_layers"]
        params.monodepth.grad_checkpointing = self.settings["monodepth_grad_checkpointing"]
        params.monodepth.use_patch_overlap = self.settings["monodepth_use_patch_overlap"]
        
        # Monodepth adaptor parameters
        params.monodepth_adaptor.encoder_features = self.settings["monodepth_adaptor_encoder_features"]
        params.monodepth_adaptor.decoder_features = self.settings["monodepth_adaptor_decoder_features"]
        
        return params



