"""
Prompt templates for classification tasks.

This module contains prompt templates for various classification tasks
using large language models.
"""

# Biological scale classification prompt template
SCALE_CLASSIFICATION_PROMPT = """
You are a scientific classification system analyzing biological research statements.
Your task is to classify the provided statement into the most appropriate biological scale.

The available biological scales are:
1. GENETIC: Genetic/genomic level (DNA, genes, chromosomes, nucleotides, genetic mutations, gene expression)
2. MOLECULAR: Molecular level (proteins, enzymes, metabolites, small molecules, biochemical reactions)
3. CELLULAR: Cellular level (cell types, organelles, cell signaling, cell cycle, cellular processes)
4. TISSUE: Tissue level (tissue types, histology, tissue organization, extracellular matrix)
5. ORGAN: Organ level (heart, liver, brain, kidneys, organ function and structure)
6. SYSTEM: System level (nervous system, immune system, cardiovascular system, system-wide processes)
7. ORGANISM: Whole organism level (physiology, behavior, development, aging, organism-wide processes)
8. POPULATION: Population level (epidemiology, population dynamics, public health, disease prevalence)
9. ECOSYSTEM: Ecosystem level (environmental interactions, ecological relationships, biodiversity)

For the statement below, determine the primary biological scale it addresses.
If the statement spans multiple scales, select the most central or emphasized scale.
Provide your classification as a JSON object with the following fields:
- "scale": The biological scale (one of the options above, in ALL CAPS)
- "confidence": A number between 0 and 1 indicating your confidence in this classification
- "reasoning": A brief explanation of your classification reasoning

Statement to classify:
"{statement}"

JSON Response:
"""

# Statement type classification prompt template
TYPE_CLASSIFICATION_PROMPT = """
You are a scientific classification system analyzing biological research statements.
Your task is to classify the provided statement into the most appropriate statement type.

The available statement types are:
1. CAUSAL: Causal relationship (A causes B, A leads to B, A results in B)
2. CORRELATIONAL: Correlational relationship (A is associated with B, A correlates with B)
3. DESCRIPTIVE: Descriptive statement (A has property B, A is characterized by B)
4. DEFINITIONAL: Definition (A is defined as B, A refers to B)
5. METHODOLOGICAL: Methodological statement (A is measured using B, A is analyzed by B)
6. COMPARATIVE: Comparative statement (A is greater/less than B, A differs from B)
7. INTERVENTION: Intervention statement (Treatment A affects B, Intervention A modifies B)
8. PREDICTIVE: Predictive statement (A predicts B, A can be used to forecast B)
9. HYPOTHESIS: Hypothesis statement (A might cause B, A could affect B)
10. REVIEW: Review statement (summarizing existing knowledge, literature overview)

For the statement below, determine the primary statement type it represents.
Provide your classification as a JSON object with the following fields:
- "type": The statement type (one of the options above, in ALL CAPS)
- "confidence": A number between 0 and 1 indicating your confidence in this classification
- "reasoning": A brief explanation of your classification reasoning

Statement to classify:
"{statement}"

JSON Response:
"""

# Combined classification prompt template
COMBINED_CLASSIFICATION_PROMPT = """
You are a scientific classification system analyzing biological research statements.
Your task is to classify the provided statement into both the most appropriate biological scale and statement type.

The available biological scales are:
1. GENETIC: Genetic/genomic level (DNA, genes, chromosomes, nucleotides, genetic mutations, gene expression)
2. MOLECULAR: Molecular level (proteins, enzymes, metabolites, small molecules, biochemical reactions)
3. CELLULAR: Cellular level (cell types, organelles, cell signaling, cell cycle, cellular processes)
4. TISSUE: Tissue level (tissue types, histology, tissue organization, extracellular matrix)
5. ORGAN: Organ level (heart, liver, brain, kidneys, organ function and structure)
6. SYSTEM: System level (nervous system, immune system, cardiovascular system, system-wide processes)
7. ORGANISM: Whole organism level (physiology, behavior, development, aging, organism-wide processes)
8. POPULATION: Population level (epidemiology, population dynamics, public health, disease prevalence)
9. ECOSYSTEM: Ecosystem level (environmental interactions, ecological relationships, biodiversity)

The available statement types are:
1. CAUSAL: Causal relationship (A causes B, A leads to B, A results in B)
2. CORRELATIONAL: Correlational relationship (A is associated with B, A correlates with B)
3. DESCRIPTIVE: Descriptive statement (A has property B, A is characterized by B)
4. DEFINITIONAL: Definition (A is defined as B, A refers to B)
5. METHODOLOGICAL: Methodological statement (A is measured using B, A is analyzed by B)
6. COMPARATIVE: Comparative statement (A is greater/less than B, A differs from B)
7. INTERVENTION: Intervention statement (Treatment A affects B, Intervention A modifies B)
8. PREDICTIVE: Predictive statement (A predicts B, A can be used to forecast B)
9. HYPOTHESIS: Hypothesis statement (A might cause B, A could affect B)
10. REVIEW: Review statement (summarizing existing knowledge, literature overview)

For the statement below, determine both the primary biological scale it addresses and the statement type it represents.
If the statement spans multiple scales, select the most central or emphasized scale.

Provide your classification as a JSON object with the following fields:
- "scale": The biological scale (one of the options above, in ALL CAPS)
- "scale_confidence": A number between 0 and 1 indicating your confidence in the scale classification
- "scale_reasoning": A brief explanation of your scale classification reasoning
- "type": The statement type (one of the options above, in ALL CAPS)
- "type_confidence": A number between 0 and 1 indicating your confidence in the type classification
- "type_reasoning": A brief explanation of your type classification reasoning

Statement to classify:
"{statement}"

JSON Response:
"""

# Batch classification prompt template
BATCH_CLASSIFICATION_PROMPT = """
You are a scientific classification system analyzing biological research statements.
Your task is to classify multiple statements into both their appropriate biological scale and statement type.

The available biological scales are:
1. GENETIC: Genetic/genomic level (DNA, genes, chromosomes, nucleotides, genetic mutations, gene expression)
2. MOLECULAR: Molecular level (proteins, enzymes, metabolites, small molecules, biochemical reactions)
3. CELLULAR: Cellular level (cell types, organelles, cell signaling, cell cycle, cellular processes)
4. TISSUE: Tissue level (tissue types, histology, tissue organization, extracellular matrix)
5. ORGAN: Organ level (heart, liver, brain, kidneys, organ function and structure)
6. SYSTEM: System level (nervous system, immune system, cardiovascular system, system-wide processes)
7. ORGANISM: Whole organism level (physiology, behavior, development, aging, organism-wide processes)
8. POPULATION: Population level (epidemiology, population dynamics, public health, disease prevalence)
9. ECOSYSTEM: Ecosystem level (environmental interactions, ecological relationships, biodiversity)

The available statement types are:
1. CAUSAL: Causal relationship (A causes B, A leads to B, A results in B)
2. CORRELATIONAL: Correlational relationship (A is associated with B, A correlates with B)
3. DESCRIPTIVE: Descriptive statement (A has property B, A is characterized by B)
4. DEFINITIONAL: Definition (A is defined as B, A refers to B)
5. METHODOLOGICAL: Methodological statement (A is measured using B, A is analyzed by B)
6. COMPARATIVE: Comparative statement (A is greater/less than B, A differs from B)
7. INTERVENTION: Intervention statement (Treatment A affects B, Intervention A modifies B)
8. PREDICTIVE: Predictive statement (A predicts B, A can be used to forecast B)
9. HYPOTHESIS: Hypothesis statement (A might cause B, A could affect B)
10. REVIEW: Review statement (summarizing existing knowledge, literature overview)

For each statement below, determine both the primary biological scale it addresses and the statement type it represents.
If a statement spans multiple scales, select the most central or emphasized scale.

Provide your classifications as a JSON array where each element is an object with the following fields:
- "statement_id": The ID of the statement (provided with each statement)
- "scale": The biological scale (one of the options above, in ALL CAPS)
- "scale_confidence": A number between 0 and 1 indicating your confidence in the scale classification
- "type": The statement type (one of the options above, in ALL CAPS)
- "type_confidence": A number between 0 and 1 indicating your confidence in the type classification

Statements to classify:
{statements}

JSON Response:
"""

# Validation prompt template
VALIDATION_PROMPT = """
You are a scientific validation system reviewing classifications of biological research statements.
Your task is to validate whether the provided classification is accurate and appropriate.

The statement and its classification are:

Statement: "{statement}"

Classification:
- Biological Scale: {scale}
- Scale Confidence: {scale_confidence}
- Statement Type: {type}
- Type Confidence: {type_confidence}

Please review this classification and determine if it is accurate. Consider:
1. Does the biological scale correctly reflect the primary level of biological organization in the statement?
2. Does the statement type correctly capture the nature of the claim being made?
3. Are the confidence scores reasonable given the clarity and specificity of the statement?

Provide your validation as a JSON object with the following fields:
- "is_valid": Boolean (true/false) indicating whether the classification is valid
- "scale_feedback": Your feedback on the scale classification (if any issues)
- "type_feedback": Your feedback on the type classification (if any issues)
- "suggested_scale": Your suggested scale if the original is incorrect (use the same scale categories)
- "suggested_type": Your suggested type if the original is incorrect (use the same type categories)
- "confidence_feedback": Your feedback on the confidence scores
- "reasoning": A brief explanation of your validation reasoning

JSON Response:
"""
