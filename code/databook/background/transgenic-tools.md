# Transgenic tools 

There are a large number of transgenic tools available that enable scientists to visualize, record, and manipulate cells in the mouse. We will briefly describe the general transgenic approaches that we use here, but this is not an exhaustive explanation of this full space.

## Cre/lox recombination approaches
The Cre/lox recombination system is a conditional approach that allows genes to be removed or expressed within specific tissues or cell types. Cre is a site-specific recombinase that drives the recombination of DNA specifically at lox-P sites. Engineering loxP on either side of a gene of interest in a cell that expresses Cre will result in that gene being removed from that cell. This technique can be used to induce the expression of a gene of interest by having a loxP-STOP-loxP sequence in front of the gene of interest. Without Cre, this gene will not be expressed due to the STOP sequence. But when Cre is present, the STOP sequence is removed, and the gene will be expressed. This is how we have used Cre lines in these experiments to drive the expression of chosen reporters.

## Reporters used here

<b>Ai93</b>
: TITL-GCaMP6f-D. Cre/Tet dependent fluorescent GCaMP6f indicator expressing GCaMP6 <i>fast</i>. This has lower expression that the Ai148 described below and is often used alongside Camk2a-tTA to enhance the expression in excitatory neurons.

<b>Ai94</b>
: TITL-GCaMP6s;Rosa26-ZtTA. Cre/Tet dependent fluorescent GCaMP6s indicator expressing GCaMP6 <i>slow</i>. This has lower expression that the Ai162 described below and is often used alongside Camk2a-tTA to enhance the expression in excitatory neurons.

<b>Ai148</b>
: TIT2L-GC6f-ICL-tTA2_D. Cre/Tet dependent fluorescent GCaMP6f indicator expressing GCaMP6 <i>fast</i>. This is a second generation reporter that uses a new TIGRE2 construct that drives higher expression. 

<b>Ai162</b>
: TIT2L-GC6s-ICL-tTA2_D. Cre/Tet dependent fluorescent GCaMP6s indicator expressing GCaMP6 <i>slow</i>. This is a second generation reporter that uses a new TIGRE2 construct that drives higher expression. 


{what are the ChR2 reporters?}


## Promoters used here

Promoters are often expressed pretty broadly across the brain. Here we've focused on describing the expression pattern found in the regions we have been targeting in the experiments in which we used these tools. 

<b>Camk2a-tTA</b>
:

<b>Cux2-CreERT2</b>
: In cortex, drives expression in excitatory neurons in layer 2/3 and 4.

<b>Emx1-IRES-Cre</b>
: In cortex, a pan-excitatory driver - drives expression in excitatory neurons across all layers. Imaged here in layer 2/3, 4, and 5. Emx1-IRES-Cre;Camk2a-tTA;Ai93 and Emx1-IRES-Cre;Camk2a-tTA;Ai94 mice were found to exhibit inter-ictal events suggesting that the dense expression of GCaMP6 throughout development could be disrupting normal physiological activity. {refererence}

<b>Fezf2-CreER</b>
: In cortex, drives expression in corticofugal excitatory neurons in layer 5.

<b>Nr5a1-Cre</b>
: In cortex, drives expression in excitatory nerons in layer 6.

<b>Ntsr1-Cre_GN220</b>
: In cortex, drives expression in a sub-population of excitatory neurons in layer 4.

<b>Pvalb-IRES-Cre</b>
: Drives expression in Parvalbumin inhibitory interneurons.

<b>Rbp4-IRES2-Cre</b>
: In cortex, drives expression in excitatory neurons in layer 5.

<b>Rorb-IRES2-Cre</b>
: In cortex, drives expression in a sub-population of excitatory neurons in layer 4.

<b>Scnn1a-Tg3-Cre</b>
: In cortex, drives expression in a sub-population of excitatory neurons in layer 4. Only found in primary sensory areas (e.g. VISp)

<b>Slc17a7-IRES2-Cre</b>
: In cortex, a pan-excitatory driver - drives expression in excitatory neurons across all layers. Imaged here in layer 2/3, 4, and 5. 

<b>Sst-IRES-Cre</b>
: Drives expression in Somatostatin inhibitory interneurons.

<b>Tlx3-Cre_PL56</b>
: In cortex, drives expression in cortico-cortical projecting excitatory neurons in layer 5.

<b>Vip-IRES-Cre</b>
: Drives expression in Vasoactive Intestinal Peptide inhibitory interneurons.
