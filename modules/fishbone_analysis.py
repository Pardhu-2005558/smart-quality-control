
def generate_fishbone_causes(defect_type):

    # Suggested causes for different defect types
    causes = {
        "Scratch": {
            "Man": ["Improper product handling", "Operator handling error"],
            "Machine": ["Rough machine surface", "Unwanted machine contact"],
            "Method": ["Incorrect loading procedure", "Improper production process"],
            "Material": ["Sharp material edges", "Contaminated raw material"],
            "Measurement": ["Visual inspection error", "Missed surface inspection"],
            "Environment": ["Dust particles", "Unclean production area"]
        },

        "Crack": {
            "Man": ["Improper handling", "Incorrect machine operation"],
            "Machine": ["Excessive machine pressure", "Machine vibration"],
            "Method": ["Excessive production force", "Incorrect processing procedure"],
            "Material": ["Brittle material", "Poor material quality"],
            "Measurement": ["Incorrect inspection", "Crack detection error"],
            "Environment": ["Temperature fluctuations", "Unsuitable storage conditions"]
        },

        "Dimension Error": {
            "Man": ["Incorrect machine setup", "Operator adjustment error"],
            "Machine": ["Machine calibration error", "Tool wear"],
            "Method": ["Incorrect production parameters", "Improper measurement procedure"],
            "Material": ["Material shrinkage", "Material expansion"],
            "Measurement": ["Inaccurate measuring instrument", "Measurement reading error"],
            "Environment": ["Temperature variation", "Humidity variation"]
        },

        "Packaging Error": {
            "Man": ["Incorrect packing", "Operator packaging error"],
            "Machine": ["Sealing machine malfunction", "Labeling machine error"],
            "Method": ["Incorrect packaging procedure", "Improper packaging sequence"],
            "Material": ["Damaged packaging material", "Poor packaging quality"],
            "Measurement": ["Incorrect final inspection", "Packaging quantity error"],
            "Environment": ["Moisture exposure", "Improper storage conditions"]
        }
    }

    default_causes = {
        "Man": ["Operator handling error", "Insufficient training"],
        "Machine": ["Machine malfunction", "Equipment maintenance issue"],
        "Method": ["Incorrect work procedure", "Process variation"],
        "Material": ["Poor material quality", "Material contamination"],
        "Measurement": ["Inspection error", "Instrument calibration issue"],
        "Environment": ["Temperature variation", "Unclean workplace"]
    }

    return causes.get(defect_type, default_causes)
