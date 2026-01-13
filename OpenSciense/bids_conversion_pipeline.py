#!/usr/bin/env python3
"""
BIDS Conversion Pipeline for Neuroimaging Volumetric Data

This script converts CSV-formatted brain volumetric measurements into 
BIDS-compliant derivative format for sharing via OpenNeuro or similar repositories.

Author: Gal Gvili & Tamir Rahamim
Date: 2026-01-03
"""

import pandas as pd
import json
import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BRAIN_REGIONS = ['A8m', 'A9l', 'A6dl', 'A10m', 'mAmyg', 'lAmyg', 'rHipp', 'cHipp']
HEMISPHERES = ['L', 'R']
TISSUE_TYPES = ['Vgm', 'Vwm', 'Vcsf']

def create_directory_structure(base_path, subject_id, session_id):
    """
    Create BIDS-compliant directory structure for derivatives.
    
    Parameters:
    -----------
    base_path : str
        Base directory for the BIDS dataset
    subject_id : str
        Subject identifier (e.g., 'sub-1001')
    session_id : str
        Session identifier (e.g., 'ses-pre')
    
    Returns:
    --------
    Path
        Path to the subject's anatomical directory
        
    Raises:
    -------
    OSError
        If directory creation fails
        
    Example:
    --------
    >>> anat_dir = create_directory_structure('.', 'sub-1001', 'ses-pre')
    >>> print(anat_dir)
    derivatives/bna_volumes/sub-1001/ses-pre/anat
    """
    try:
        anat_dir = Path(base_path) / 'derivatives' / 'bna_volumes' / subject_id / session_id / 'anat'
        anat_dir.mkdir(parents=True, exist_ok=True)
        return anat_dir
    except OSError as e:
        logger.error(f"Failed to create directory {anat_dir}: {e}")
        raise

def convert_csv_to_bids_tsv(input_csv, output_dir, subject_id, session_id):
    """
    Convert neuroimaging CSV data to BIDS derivative TSV format.
    
    Parameters:
    -----------
    input_csv : str
        Path to input CSV file with brain volume data
    output_dir : str
        Output directory for BIDS dataset
    subject_id : str
        Subject identifier
    session_id : str
        Session identifier
    
    Returns:
    --------
    str or None
        Path to created TSV file, or None if conversion failed
        
    Raises:
    -------
    FileNotFoundError
        If input CSV file doesn't exist
    ValueError
        If required columns are missing from CSV
        
    Example:
    --------
    >>> tsv_file = convert_csv_to_bids_tsv(
    ...     'Data/sample_data.csv', 
    ...     '.', 
    ...     'sub-1001', 
    ...     'ses-pre'
    ... )
    """
    # Validate input file exists
    input_path = Path(input_csv)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_csv}")
        return None
    
    try:
        # Read input CSV
        df = pd.read_csv(input_csv)
    except pd.errors.EmptyDataError:
        logger.error(f"Input file is empty: {input_csv}")
        return None
    except Exception as e:
        logger.error(f"Failed to read CSV file: {e}")
        return None
    
    # Validate required columns
    required_cols = ['subject num', 'time']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        return None
    
    # Filter data for specific subject and session
    subject_num = int(subject_id.replace('sub-', ''))
    subject_data = df[df['subject num'] == subject_num]
    
    if subject_data.empty:
        logger.warning(f"No data found for subject {subject_id}")
        return None
    
    # Determine session based on 'time' column
    time_value = session_id.replace('ses-', '')
    subject_data = subject_data[subject_data['time'] == time_value]
    
    if subject_data.empty:
        logger.warning(f"No data found for {subject_id} {session_id}")
        return None
    
    # Extract volumetric columns
    volume_data = []
    
    # Process each brain region
    for region in BRAIN_REGIONS:
        for hemisphere in HEMISPHERES:
            # Column names in format: "A8m_L Vgm", "A8m_L Vwm", "A8m_L Vcsf"
            vgm_col = f"{region}_{hemisphere} Vgm"
            vwm_col = f"{region}_{hemisphere} Vwm"
            vcsf_col = f"{region}_{hemisphere} Vcsf"
            
            # Check if all tissue type columns exist
            if all(col in subject_data.columns for col in [vgm_col, vwm_col, vcsf_col]):
                try:
                    volume_data.append({
                        'region': region,
                        'hemisphere': hemisphere,
                        'gray_matter_volume': float(subject_data[vgm_col].values[0]),
                        'white_matter_volume': float(subject_data[vwm_col].values[0]),
                        'csf_volume': float(subject_data[vcsf_col].values[0])
                    })
                except (IndexError, ValueError) as e:
                    logger.warning(f"Failed to extract data for {region}_{hemisphere}: {e}")
                    continue
            else:
                logger.warning(f"Missing columns for region {region}_{hemisphere}")
    
    if not volume_data:
        logger.error(f"No valid volumetric data extracted for {subject_id} {session_id}")
        return None
    
    # Create BIDS derivative dataframe
    bids_df = pd.DataFrame(volume_data)
    
    # Create output directory
    try:
        anat_dir = create_directory_structure(output_dir, subject_id, session_id)
    except OSError:
        return None
    
    # Save as TSV
    output_file = anat_dir / f"{subject_id}_{session_id}_space-BNA_volumes.tsv"
    try:
        bids_df.to_csv(output_file, sep='\t', index=False)
        logger.info(f"Created: {output_file}")
        return str(output_file)
    except Exception as e:
        logger.error(f"Failed to write TSV file: {e}")
        return None

def create_sidecar_json(output_dir, subject_id, session_id):
    """
    Create BIDS sidecar JSON file with column descriptions.
    
    Parameters:
    -----------
    output_dir : str
        Output directory for BIDS dataset
    subject_id : str
        Subject identifier
    session_id : str
        Session identifier
        
    Returns:
    --------
    bool
        True if successful, False otherwise
        
    Example:
    --------
    >>> success = create_sidecar_json('.', 'sub-1001', 'ses-pre')
    """
    sidecar = {
        "region": {
            "LongName": "Brain Region",
            "Description": "Brainnetome Atlas (BNA) region label"
        },
        "hemisphere": {
            "LongName": "Hemisphere",
            "Description": "Brain hemisphere",
            "Levels": {
                "L": "Left hemisphere",
                "R": "Right hemisphere"
            }
        },
        "gray_matter_volume": {
            "LongName": "Gray Matter Volume",
            "Description": "Volume of gray matter tissue in the region",
            "Units": "mm^3"
        },
        "white_matter_volume": {
            "LongName": "White Matter Volume",
            "Description": "Volume of white matter tissue in the region",
            "Units": "mm^3"
        },
        "csf_volume": {
            "LongName": "Cerebrospinal Fluid Volume",
            "Description": "Volume of CSF in the region",
            "Units": "mm^3"
        }
    }
    
    anat_dir = Path(output_dir) / 'derivatives' / 'bna_volumes' / subject_id / session_id / 'anat'
    json_file = anat_dir / f"{subject_id}_{session_id}_space-BNA_volumes.json"
    
    try:
        with open(json_file, 'w') as f:
            json.dump(sidecar, f, indent=4)
        logger.info(f"Created: {json_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to write JSON file: {e}")
        return False

def create_participants_files(questionnaire_csv, volumetric_csv, output_dir):
    """
    Create BIDS participants.tsv and participants.json files.
    
    Parameters:
    -----------
    questionnaire_csv : str
        Path to questionnaire metadata CSV
    volumetric_csv : str
        Path to volumetric data CSV (contains group assignment)
    output_dir : str
        Output directory for BIDS dataset
        
    Returns:
    --------
    bool
        True if successful, False otherwise
        
    Raises:
    -------
    FileNotFoundError
        If input files don't exist
    ValueError
        If required columns are missing
        
    Example:
    --------
    >>> success = create_participants_files(
    ...     'Data/questionnaire_metadata.csv',
    ...     'Data/sample_data.csv',
    ...     '.'
    ... )
    """
    # Validate input files
    questionnaire_path = Path(questionnaire_csv)
    volumetric_path = Path(volumetric_csv)
    
    if not questionnaire_path.exists():
        logger.error(f"Questionnaire file not found: {questionnaire_csv}")
        return False
    
    if not volumetric_path.exists():
        logger.error(f"Volumetric data file not found: {volumetric_csv}")
        return False
    
    try:
        # Read questionnaire data
        quest_df = pd.read_csv(questionnaire_csv)
        
        # Read volumetric data for group assignment
        vol_df = pd.read_csv(volumetric_csv)
        
        # Validate required columns
        required_quest_cols = ['subject num', 'age', 'is_female', 'is_right_handed', 'additional_languages']
        missing_quest_cols = [col for col in required_quest_cols if col not in quest_df.columns]
        if missing_quest_cols:
            logger.error(f"Missing questionnaire columns: {missing_quest_cols}")
            return False
        
        if 'group' not in vol_df.columns:
            logger.error("Missing 'group' column in volumetric data")
            return False
        
        # Get unique subject-group mapping from volumetric data
        subject_groups = vol_df[['subject num', 'group']].drop_duplicates()
        
        # Merge questionnaire data with group information
        merged_df = pd.merge(quest_df, subject_groups, on='subject num', how='left')
        
        # Create participants dataframe
        participants = pd.DataFrame({
            'participant_id': merged_df['subject num'].apply(lambda x: f'sub-{x}'),
            'age': merged_df['age'],
            'sex': merged_df['is_female'].map({0: 'M', 1: 'F'}),
            'group': merged_df['group'],
            'handedness': merged_df['is_right_handed'].map({0: 'L', 1: 'R'}),
            'additional_languages': merged_df['additional_languages']
        })
        
        # Save participants.tsv
        participants_file = Path(output_dir) / 'participants.tsv'
        participants.to_csv(participants_file, sep='\t', index=False)
        logger.info(f"Created: {participants_file}")
        
        # Create participants.json
        participants_json = {
            "participant_id": {
                "Description": "Unique identifier for the participant in BIDS format",
                "LongName": "Participant Identifier"
            },
            "age": {
                "Description": "Age of participant at time of data collection",
                "Units": "years"
            },
            "sex": {
                "Description": "Biological sex of participant",
                "Levels": {
                    "M": "male",
                    "F": "female"
                }
            },
            "group": {
                "Description": "Experimental group assignment",
                "Levels": {
                    "control": "Control group participants",
                    "patient": "Patient group participants"
                }
            },
            "handedness": {
                "Description": "Dominant hand of participant",
                "Levels": {
                    "R": "right-handed",
                    "L": "left-handed"
                }
            },
            "additional_languages": {
                "Description": "Additional languages spoken by participant at basic conversational level or above",
                "LongName": "Additional Languages"
            }
        }
        
        json_file = Path(output_dir) / 'participants.json'
        with open(json_file, 'w') as f:
            json.dump(participants_json, f, indent=4)
        logger.info(f"Created: {json_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create participants files: {e}")
        return False

def main():
    """
    Main conversion pipeline execution.
    """
    logger.info("=" * 60)
    logger.info("BIDS Conversion Pipeline for Neuroimaging Data")
    logger.info("=" * 60)
    
    # Configuration
    input_data_csv = 'Data/sample_data.csv'
    input_questionnaire_csv = 'Data/questionnaire_metadata.csv'
    output_dir = '.'
    
    # Subject and session information
    subjects = [
        {'id': 'sub-1001', 'sessions': ['ses-pre']},
        {'id': 'sub-1002', 'sessions': ['ses-pre']},
        {'id': 'sub-1003', 'sessions': ['ses-post']}
    ]
    
    # Step 1: Create participants files
    logger.info("\nStep 1: Creating participants files...")
    success = create_participants_files(input_questionnaire_csv, input_data_csv, output_dir)
    if not success:
        logger.error("Failed to create participants files. Exiting.")
        sys.exit(1)
    
    # Step 2: Convert volumetric data to BIDS format
    logger.info("\nStep 2: Converting volumetric data to BIDS format...")
    conversion_count = 0
    failed_count = 0
    
    for subject in subjects:
        subject_id = subject['id']
        for session_id in subject['sessions']:
            logger.info(f"\nProcessing {subject_id} {session_id}...")
            
            # Convert data to BIDS TSV
            tsv_file = convert_csv_to_bids_tsv(
                input_data_csv, 
                output_dir, 
                subject_id, 
                session_id
            )
            
            # Create sidecar JSON
            if tsv_file:
                if create_sidecar_json(output_dir, subject_id, session_id):
                    conversion_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Conversion complete!")
    logger.info("=" * 60)
    logger.info(f"Successfully converted: {conversion_count} subject-session pairs")
    if failed_count > 0:
        logger.warning(f"Failed conversions: {failed_count}")
    
    logger.info("\nNext steps:")
    logger.info("1. Validate BIDS structure using: bids-validator .")
    logger.info("2. Review README and dataset_description.json")
    logger.info("3. Upload to OpenNeuro or your chosen repository")
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
