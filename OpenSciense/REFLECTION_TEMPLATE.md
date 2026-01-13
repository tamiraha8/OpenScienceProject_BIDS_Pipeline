# Open Science Data Sharing Project - Reflection

**Student Names:** Gal Gvili & Tamir Rahamim  
**Date:** January 2026  
**Course:** Open Science Data Sharing  

---

## 1. Data Description and Structure (200-300 words)

### Data Type
This dataset contains **brain volumetric measurements** derived from structural MRI scans. The data represents processed neuroimaging derivatives rather than raw MRI images.

### Data Structure
The dataset includes:
- **3 participants** (subjects 1001, 1002, 1003)
- **Demographic information**: age, sex, group assignment, handedness
- **Brain measurements**: Volumetric data from 8 bilateral brain regions using Brainnetome Atlas (BNA) parcellation
- **Tissue types**: Three volume measurements per region (gray matter, white matter, CSF)
- **Sessions**: Pre/post measurements for longitudinal analysis

### Brain Regions Analyzed
- **Prefrontal cortex**: A8m, A9l, A6dl, A10m
- **Subcortical structures**: 
  - Amygdala (medial and lateral)
  - Hippocampus (rostral and caudal)

### Original Format
Data originated as CSV files with:
- Wide format with columns for each region-hemisphere-tissue combination
- Column naming convention: `RegionName_Hemisphere TissueType` (e.g., "A8m_L Vgm")
- Separate demographic/questionnaire metadata file

---

## 2. Chosen Format and Repository (200-300 words)

### Format: BIDS (Brain Imaging Data Structure)

**Why BIDS?**
1. **Standard for neuroimaging**: BIDS is the accepted standard for organizing and sharing neuroimaging data
2. **Repository compatibility**: Required for OpenNeuro and widely accepted across neuroscience repositories
3. **Machine-readable**: Structured format with JSON metadata enables automated processing
4. **Community adoption**: Extensive tooling and validation support

### Specific Implementation: BIDS Derivatives

Since our data consists of processed volumetric measurements (not raw MRI scans), we implemented the **BIDS derivatives** specification:
- `DatasetType: "derivative"` in dataset_description.json
- Organized under `derivatives/bna_volumes/` directory
- Each subject-session combination has separate TSV files with sidecar JSON metadata

### Repository Choice: OpenNeuro

**Reasons for choosing OpenNeuro:**
- Free, open-access platform specifically designed for neuroimaging
- BIDS-native (automatic validation)
- Assigns DOIs for citability
- Integrates with analysis platforms (e.g., Brainlife)
- Long-term preservation guarantee

**Alternative considered:** Generic repositories like Zenodo were considered but OpenNeuro's neuroimaging-specific features and BIDS validation made it the superior choice.

---

## 3. Challenges Faced (300-500 words)

### Challenge 1: Format Conversion from CSV to BIDS

**Problem:** The original data was in wide-format CSV (one row per subject-session with many columns), while BIDS derivatives use long-format TSV (one row per brain region).

**Solution:** Created Python conversion script that:
- Parses CSV column names to extract region, hemisphere, and tissue type
- Transforms wide format to long format
- Generates BIDS-compliant filenames with proper entities

**Code snippet:**
```python
# Column format: "A8m_L Vgm" → region='A8m', hemisphere='L', tissue='Vgm'
for region in regions:
    for hemisphere in ['L', 'R']:
        vgm_col = f"{region}_{hemisphere} Vgm"
        # Extract and reorganize...
```

### Challenge 2: Metadata Documentation

**Problem:** BIDS requires extensive JSON sidecar files documenting every data column, but our original data had minimal documentation.

**Solution:** 
- Created comprehensive participants.json defining demographic variables
- Generated sidecar JSON for each volumetric TSV file
- Documented brain region naming conventions in README
- Added units (mm³) and descriptions for all measurements

**Lesson learned:** Good documentation takes significant time but is essential for data reusability.

### Challenge 3: Determining Appropriate BIDS Entity Labels

**Problem:** BIDS has specific naming conventions (e.g., `sub-<label>_ses-<label>_space-<label>_desc-<label>`), and choosing appropriate entities for derivative data was unclear.

**Solution:** 
- Used `space-BNA` entity to indicate Brainnetome Atlas coordinate space
- Standardized session labels as `ses-pre` and `ses-post`
- Reviewed BIDS examples and specification documents for derivatives

### Challenge 4: Validating BIDS Compliance

**Problem:** Ensuring the dataset actually conforms to BIDS standards.

**Solution planned:** 
- Would use `bids-validator` command-line tool
- For derivatives, some validation warnings are expected and acceptable
- Manual review against BIDS specification v1.8.0

### Challenge 5: Code Quality and Error Handling

**Problem:** Initial code lacked proper error handling, input validation, and had hardcoded values that could cause issues with different datasets.

**Solution:**
- Added comprehensive try-except blocks for all file I/O operations
- Implemented input validation to check for required columns before processing
- Defined brain regions and tissue types as module-level constants for maintainability
- Added logging framework (Python's `logging` module) instead of simple print statements
- Included detailed docstrings with usage examples for all functions
- Fixed group assignment to read from actual data source rather than hardcoding

**Code improvements made:**
```python
# Before: Hardcoded group assignment
'group': 'control',  # Simplified - adjust based on your data

# After: Read from actual data
subject_groups = vol_df[['subject num', 'group']].drop_duplicates()
merged_df = pd.merge(quest_df, subject_groups, on='subject num', how='left')
participants['group'] = merged_df['group']
```

**Impact:** The code is now more robust, maintainable, and production-ready. It provides clear error messages when issues occur and can handle edge cases gracefully.

---

## 4. How the Guide Helped (and Where It Failed) (200-300 words)

### How the Guide Helped

The **FMRI Data Sharing via OpenNeuro and BIDS** guide was instrumental in several areas:

1. **BIDS Structure Overview**: Clearly explained the directory hierarchy and naming conventions
2. **Required Files**: Listed mandatory files (dataset_description.json, README, CHANGES, participants.tsv)
3. **JSON Metadata**: Provided examples of properly formatted sidecar JSON files
4. **OpenNeuro Upload Process**: Step-by-step instructions for dataset submission

**Most valuable sections:**
- BIDS entity naming rules (sub-, ses-, space-, etc.)
- Examples of dataset_description.json
- Explanation of derivatives vs. raw data

### Where the Guide Failed to Assist

1. **Derivatives Specifics**: The guide focused primarily on raw fMRI data, with limited coverage of derivative datasets. More examples of processed/analyzed data would help.

2. **CSV-to-BIDS Conversion**: No guidance on converting existing tabular data to BIDS format. Had to develop conversion strategy independently.

3. **Volumetric Data**: Guide emphasized task-based fMRI and functional data, with less coverage of structural/anatomical derivatives.

4. **Custom Atlases**: Limited guidance on documenting non-standard brain parcellations (BNA in our case vs. more common Freesurfer/AAL).

### Additional Resources Used

- **BIDS Specification** (https://bids-specification.readthedocs.io): Official documentation for derivatives
- **BIDS Examples** (GitHub): Reference datasets showing derivative organization
- **OpenNeuro** existing datasets: Reviewed similar volumetric studies for formatting patterns

---

## 5. Reflection on the Process (200-300 words)

### Key Learnings

1. **Data standardization requires significant effort**: Converting from lab-specific formats to community standards is time-consuming but worthwhile for reproducibility.

2. **Documentation is as important as data**: Well-described metadata (JSON sidecars, README files) transforms data from unusable to valuable.

3. **FAIR principles in practice**: This exercise demonstrated how Findable, Accessible, Interoperable, and Reusable (FAIR) data sharing requires intentional structure.

### Future Applications

This pipeline is now reusable for future neuroimaging studies in our lab:
- Script can process new subjects automatically
- BIDS structure ensures compatibility with analysis tools
- Documentation template speeds up dataset preparation

### Impact on Research Practice

**Before:** Data stored in lab-specific formats, accessible only to original researchers.

**After:** Data organized for immediate sharing, with clear documentation enabling others to understand and reuse our measurements.

### Recommendations for Others

1. **Start with BIDS early**: Organizing data in BIDS format from the beginning is easier than retroactive conversion
2. **Use existing tools**: Leverage BIDS converters when available rather than writing custom scripts
3. **Validate frequently**: Run bids-validator throughout the process, not just at the end
4. **Over-document**: If uncertain whether to include information, include it—more metadata is always better

---

## 6. Conclusion (100-150 words)

This project successfully transformed lab-specific neuroimaging data into a BIDS-compliant, openly shareable dataset ready for upload to OpenNeuro. The process required:
- Developing a conversion pipeline from CSV to BIDS derivatives format
- Creating comprehensive metadata documentation
- Following community standards for neuroimaging data organization

While challenging—particularly regarding derivative data specifics and format conversion—the effort creates long-term value through enhanced data reusability and reproducibility. The resulting pipeline is now a reusable asset for our lab, streamlining future data sharing and contributing to the open science ecosystem.

**Word count:** ~1,350 words

---

## Appendix: Files Submitted

1. **BIDS Dataset**: `OpenScience/` directory containing full BIDS structure
2. **Conversion Pipeline**: `bids_conversion_pipeline.py` 
3. **This Reflection**: `REFLECTION_TEMPLATE.md`
