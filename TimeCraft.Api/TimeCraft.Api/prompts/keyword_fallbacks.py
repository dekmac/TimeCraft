"""
Keyword-based tag generation fallbacks for TimeCraft API.

This module contains fallback tag generation logic when LLM is not available.
"""


def get_keyword_to_tags_mapping() -> dict:
    """Get the mapping of keywords to predefined tag lists."""
    return {
        # Food & Dairy Processing
        'milk': ['PASTEURIZER_TEMP_01', 'HOMOGENIZER_PRESS_02', 'TANK_LEVEL_RAW_MILK', 'FILLING_LINE_SPEED', 'CIP_FLOW_RATE'],
        'dairy': ['SEPARATOR_SPEED_01', 'CREAM_FAT_CONTENT', 'PASTEURIZATION_TEMP', 'COOLING_TEMP_02', 'PACKAGE_COUNT'],
        'pasteurize': ['PASTEURIZER_INLET_TEMP', 'PASTEURIZER_OUTLET_TEMP', 'PASTEURIZER_FLOW_RATE', 'PASTEURIZER_PRESSURE'],
        'cheese': ['CURD_TEMP_01', 'WHEY_PH_02', 'AGING_HUMIDITY_03', 'BRINE_CONCENTRATION', 'CUTTING_SPEED'],
        'yogurt': ['FERMENTATION_TEMP', 'CULTURE_PH', 'INCUBATION_TIME', 'COOLING_RATE', 'MIXING_SPEED'],
        
        # Manufacturing & Production
        'manufacturing': ['MOTOR_VIBRATION_A1', 'HYDRAULIC_PRESS_01', 'CONVEYOR_SPEED_LINE3', 'TEMP_BEARING_B2', 'FLOW_COOLANT_C1'],
        'factory': ['PRODUCTION_RATE_01', 'MACHINE_EFFICIENCY_02', 'POWER_CONSUMPTION_03', 'CYCLE_TIME_04', 'REJECT_COUNT_05'],
        'assembly': ['TORQUE_WRENCH_01', 'POSITION_ROBOT_ARM', 'CYCLE_TIME_STATION', 'QUALITY_CHECK_PASS', 'PARTS_COUNT'],
        'production': ['THROUGHPUT_RATE', 'DOWNTIME_MINUTES', 'OEE_PERCENTAGE', 'DEFECT_RATE', 'ENERGY_USAGE'],
        'conveyor': ['BELT_SPEED_01', 'MOTOR_CURRENT_02', 'BELT_TENSION_03', 'ITEM_COUNT_04', 'TRACKING_POSITION'],
        
        # Chemical Processing
        'chemical': ['REACTOR_TEMP_R101', 'DISTILLATION_PRESS_C201', 'PH_ANALYZER_A301', 'PUMP_FLOW_P301', 'LEVEL_TANK_T101'],
        'reactor': ['REACTOR_PRESSURE', 'REACTOR_TEMPERATURE', 'AGITATOR_SPEED', 'REACTION_PH', 'CATALYST_FEED'],
        'distillation': ['COLUMN_TEMP_TOP', 'COLUMN_TEMP_BOTTOM', 'REFLUX_RATIO', 'REBOILER_DUTY', 'PRODUCT_PURITY'],
        
        # HVAC & Building Systems
        'hvac': ['CHILLER_TEMP_SUPPLY', 'AHU_FLOW_RATE_01', 'ROOM_HUMIDITY_ZONE2', 'FAN_SPEED_F301', 'DAMPER_POS_D201'],
        'chiller': ['CHILLER_COP', 'EVAP_TEMP', 'CONDENSER_TEMP', 'REFRIGERANT_PRESS', 'COOLING_LOAD'],
        'cooling': ['COOLING_WATER_TEMP', 'COOLING_TOWER_FAN', 'HEAT_EXCHANGER_FLOW', 'GLYCOL_CONCENTRATION'],
        
        # Power & Electrical
        'power': ['GENERATOR_VOLTAGE_G1', 'TURBINE_SPEED_T1', 'TRANSFORMER_TEMP_TR1', 'CURRENT_LOAD_L1', 'FREQUENCY_GRID_F1'],
        'generator': ['GEN_POWER_OUTPUT', 'GEN_FREQUENCY', 'GEN_VOLTAGE', 'GEN_CURRENT', 'GEN_POWER_FACTOR'],
        'electrical': ['VOLTAGE_L1', 'CURRENT_L2', 'POWER_FACTOR_L3', 'HARMONIC_DISTORTION', 'ENERGY_METER'],
        
        # Water Treatment
        'water': ['PUMP_FLOW_P101', 'FILTER_PRESS_F201', 'CHLORINE_LEVEL_C101', 'TURBIDITY_T301', 'PH_EFFLUENT_PH201'],
        'treatment': ['CLARIFIER_LEVEL', 'SLUDGE_DENSITY', 'DISSOLVED_OXYGEN', 'CONDUCTIVITY', 'ALKALINITY'],
        'filtration': ['FILTER_DIFFERENTIAL_PRESS', 'BACKWASH_FLOW', 'FILTRATE_TURBIDITY', 'MEDIA_DEPTH'],
        
        # Oil & Gas
        'oil': ['PIPELINE_PRESS_PP101', 'FLOW_CRUDE_F201', 'TEMP_DISTILLATION_TD301', 'LEVEL_TANK_LT401', 'VALVE_POS_V501'],
        'gas': ['GAS_FLOW_RATE', 'PIPELINE_PRESSURE', 'COMPRESSOR_SPEED', 'MOISTURE_CONTENT', 'HEATING_VALUE'],
        'refinery': ['CRUDE_FLOW_RATE', 'FURNACE_TEMP', 'CATALYST_ACTIVITY', 'PRODUCT_OCTANE', 'SULFUR_CONTENT'],
        
        # Automotive
        'automotive': ['ENGINE_RPM_E1', 'BRAKE_TEMP_B1', 'TRANSMISSION_PRESS_T1', 'FUEL_FLOW_F1', 'EXHAUST_TEMP_EX1'],
        'engine': ['ENGINE_COOLANT_TEMP', 'OIL_PRESSURE', 'THROTTLE_POSITION', 'MANIFOLD_PRESSURE', 'IGNITION_TIMING'],
        
        # Generic fallbacks
        'temperature': ['TEMPERATURE_01', 'TEMPERATURE_02', 'AMBIENT_TEMP'],
        'pressure': ['PRESSURE_GAUGE_01', 'PRESSURE_GAUGE_02', 'SYSTEM_PRESSURE'],
        'flow': ['FLOW_METER_01', 'FLOW_METER_02', 'FLOW_RATE_03'],
        'level': ['LEVEL_SENSOR_01', 'LEVEL_SENSOR_02', 'TANK_LEVEL_03'],
        'sensor': ['SENSOR_A', 'SENSOR_B', 'SENSOR_C'],
        'monitoring': ['CPU_USAGE', 'MEMORY_USAGE', 'NETWORK_TRAFFIC'],
        'iot': ['IOT_DEVICE_01', 'IOT_DEVICE_02', 'IOT_DEVICE_03']
    }


def get_generic_tags() -> list:
    """Get a list of generic industrial tags for fallback."""
    return [
        'TEMPERATURE_SENSOR_01', 'PRESSURE_GAUGE_02', 'FLOW_METER_03', 
        'LEVEL_SENSOR_04', 'VIBRATION_MONITOR_05', 'SPEED_SENSOR_06',
        'CURRENT_MONITOR_07', 'POSITION_SENSOR_08', 'HUMIDITY_SENSOR_09',
        'PH_ANALYZER_10'
    ]


def generate_tags_from_keywords(description: str, num_tags: int) -> list:
    """Generate tag names based on keyword matching."""
    keywords_to_tags = get_keyword_to_tags_mapping()
    generic_tags = get_generic_tags()
    
    tags = []
    lower_desc = description.lower()
    
    # Find matching keywords and add their tags
    for keyword, tag_list in keywords_to_tags.items():
        if keyword in lower_desc:
            tags.extend(tag_list)
            if len(tags) >= num_tags:
                break
    
    # Fill remaining slots with generic industrial tags
    while len(tags) < num_tags:
        if len(generic_tags) > (len(tags) % len(generic_tags)):
            tags.append(generic_tags[len(tags) % len(generic_tags)])
        else:
            tags.append(f'GENERIC_SENSOR_{len(tags) + 1:02d}')
    
    return tags[:num_tags]


def get_domain_specific_tags() -> dict:
    """Get domain-specific tag collections for mock responses."""
    return {
        'dairy': [
            "PASTEURIZER_INLET_TEMP", "PASTEURIZER_OUTLET_TEMP", "HOMOGENIZER_PRESSURE",
            "SEPARATOR_SPEED", "CIP_FLOW_RATE", "TANK_LEVEL_A1", "COOLING_TEMP_B2"
        ],
        'manufacturing': [
            "MOTOR_VIBRATION_M1", "HYDRAULIC_PRESSURE_H1", "CONVEYOR_SPEED_C1",
            "BEARING_TEMP_B1", "COOLANT_FLOW_CF1", "PRODUCTION_COUNT_PC1"
        ],
        'chemical': [
            "REACTOR_TEMP_R1", "CATALYST_FEED_RATE", "DISTILLATION_PRESSURE",
            "PH_ANALYZER_A1", "PUMP_FLOW_P1", "TANK_LEVEL_T1"
        ],
        'hvac': [
            "CHILLER_SUPPLY_TEMP", "AHU_FLOW_RATE_01", "ROOM_HUMIDITY_Z1",
            "FAN_SPEED_F1", "DAMPER_POSITION_D1", "COOLING_LOAD_CL1"
        ],
        'power': [
            "GENERATOR_VOLTAGE_G1", "TURBINE_SPEED_T1", "TRANSFORMER_TEMP_TR1",
            "GRID_FREQUENCY_GF1", "POWER_OUTPUT_PO1", "CURRENT_LOAD_CL1"
        ],
        'water': [
            "PUMP_FLOW_P1", "FILTER_PRESSURE_F1", "CHLORINE_LEVEL_CL1",
            "TURBIDITY_T1", "PH_EFFLUENT_PH1", "DISSOLVED_OXYGEN_DO1"
        ],
        'oil_gas': [
            "PIPELINE_PRESSURE_PP1", "CRUDE_FLOW_CF1", "DISTILLATION_TEMP_DT1",
            "COMPRESSOR_SPEED_CS1", "VALVE_POSITION_V1", "TANK_LEVEL_TL1"
        ],
        'automotive': [
            "ENGINE_RPM_E1", "BRAKE_TEMP_B1", "TRANSMISSION_PRESSURE_TP1",
            "FUEL_FLOW_FF1", "EXHAUST_TEMP_ET1", "OIL_PRESSURE_OP1"
        ],
        'bridge': [
            "VIBRATION_SENSOR_V1", "STRAIN_GAUGE_S1", "DISPLACEMENT_D1",
            "TEMPERATURE_T1", "TILT_METER_TM1", "WIND_SPEED_WS1"
        ],
        'building': [
            "STRUCTURAL_TEMP_ST1", "FOUNDATION_PRESSURE_FP1", "SWAY_MONITOR_SM1",
            "SETTLEMENT_GAUGE_SG1", "CONCRETE_STRAIN_CS1", "HUMIDITY_H1"
        ],
        'default': [
            "SENSOR_TAG_01", "SENSOR_TAG_02", "SENSOR_TAG_03",
            "MONITOR_POINT_M1", "DATA_POINT_DP1", "MEASUREMENT_TAG_MT1"
        ]
    }