# Neuroimaging Volumetric Analysis Dataset

## Overview

This dataset contains brain volumetric measurements derived from structural MRI scans using the Brainnetome Atlas (BNA) parcellation scheme. The data includes measurements from 3 participants across control and patient groups.

## Dataset Description

- **Modality**: Structural MRI (T1-weighted)
- **Processing**: Volumetric analysis using Brainnetome Atlas parcellation
- **Participants**: 3 subjects (2 control, 1 patient)
- **Sessions**: Pre and post measurements for longitudinal analysis

## Data Structure

This dataset follows the Brain Imaging Data Structure (BIDS) derivative format for processed neuroimaging data.

### Brain Regions

Brain volumetric measurements include:
- **Prefrontal cortex regions**: A8m, A9l, A6dl, A10m (bilateral)
- **Subcortical structures**: 
  - Amygdala: medial (mAmyg) and lateral (lAmyg)
  - Hippocampus: rostral (rHipp) and caudal (cHipp)

### Volume Measurements

For each brain region, three tissue volume measurements are provided:
- **Vgm**: Gray matter volume (mm³)
- **Vwm**: White matter volume (mm³)
- **Vcsf**: Cerebrospinal fluid volume (mm³)

## File Structure

```
OpenScience/
├── dataset_description.json    # Dataset metadata
├── participants.tsv            # Participant demographics
├── participants.json           # Column descriptions for participants.tsv
├── README                      # This file
├── CHANGES                     # Version history
└── derivatives/
    └── bna_volumes/
        ├── dataset_description.json
        └── sub-<ID>/
            └── ses-<session>/
                └── anat/
                    ├── sub-<ID>_ses-<session>_space-BNA_volumes.tsv
                    └── sub-<ID>_ses-<session>_space-BNA_volumes.json
```

## Participant Information

| participant_id | age | sex | group   | handedness | additional_languages |
|----------------|-----|-----|---------|------------|---------------------|
| sub-1001       | 28  | M   | control | R          | English, Hebrew     |
| sub-1002       | 34  | F   | patient | R          | English, Russian    |
| sub-1003       | 25  | M   | control | R          | English             |

## Experimental Groups

- **Control**: Healthy control participants with no neurological conditions (n=2)
- **Patient**: Patient group participants (n=1)

## Data Acquisition

Data were acquired using standard T1-weighted MPRAGE sequences and processed using automated brain parcellation pipelines.

## Usage Notes

- Volume measurements are in cubic millimeters (mm³)
- All measurements are bilateral (left and right hemispheres)
- Data quality has been verified for anatomical accuracy

## Ethics

All participants provided informed consent. This is mock data for demonstration purposes.

## Contact

For questions about this dataset, please contact the research team.

## Acknowledgements

Brain parcellation performed using the Brainnetome Atlas (BNA).
