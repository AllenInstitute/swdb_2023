# Optotagging

The purpose of this dataset is to create a ground-truth dataset of responses from known striatal cell types so that we can look for differences in their physiological properties. But how do we know if the units we pick up during ephys belong to a specific cell type? We use a technique known as "optotagging."

Briefly, the technique leverages genetic tools to express light-gated ion channels only in a specific cell type. These cells can then be identified in recordings by their responses to laser light. The following sections will give more information on how this was achieved in our experiments.

# Opsins

In order to drive spiking activity using laser light, we have to make neurons produce light-gated ion channels, herethefore referred to as "opsins." These opsins will change their conformation when exposed to specific wavelengths of light, opening a channel that allows ions to cross the cell membrane, most commonly sodium for light-triggered excitation or chloride for light-triggered inhibition.

The opsins used in this data set were:
* CoChR: a blue-light activated sodium channel
* ChrimsonR: a red-light activated sodium channel
* ChRmine: a red-light activated sodium channel
* BiPOLES: a red-light activated sodium channel paired with a blue-light activated chloride channel

# Cre lines and Cre-dependent viruses

We want to be able to drive the expression of the above opsins only in specific cell types so that we can identify them by their responses to laser. To do this, we leverage a technique called Cre-lox recombination. Briefly, the gene for Cre recombinase is inserted into the mouse genome in such a way that it is only expressed in a specific cell type. Such mice are referred to as belonging to a specific driver line (e.g. expression of Cre is only driven in a given cell type). A Cre-dependent virus is then injected into the brain, delivering the DNA encoding the opsin we want to express. The DNA delivered by this virus is not in a usable configuration unless acted upon by Cre recombinase; as such, only cells expressing Cre will end up expressing the opsin.

To determine the genotype of the animal for each session (and thus which driver line it's part of, and which cells are expressing Cre), use the following command:
```{code-cell} ipython3
import json

subject_json = 'path-to-subject-json'
with open(subject_json, 'r', ) as f:
    subject_data = json.load(f)
    
subject_data['genotype']
```
The genotype for these experiments can be one of several:
* Drd1a-Cre: This driver line drives expression of Cre in striatal direct pathway neurons (D1)
* Adora2a-Cre: This driver line drives expression of Cre in striatal indirect pathway neurons (D2)
* Chat-IRES-Cre-neo: This driver line drives expression of Cre in cholinergic neurons

# Enhancer viruses

Another method of getting opsins into cells is to use enhancer viruses. These viruses do not rely on the presense of Cre, but rather can directly target specific cell types on their own by targeting enhancer regions in the DNA that are enriched in specific cell types. More information about this technique can be found here: LINK TO PAPER

To determine which viruses were injected into a given animal, use the following commands:

```{code-cell} ipython3
import json

procedures_json = 'path-to-procedures-json'
with open(procedures_json, 'r', ) as f:
    procedures_data = json.load(f)
    
virus_names = []
    for material in procedures['injections'][0]['injection_materials']:
        virus_names.append(material['name'])
```
You will produce a list of all the shortened virus names that were injected into this mouse. There are generally multiple viruses, as we want to tag different cell types with different opsins!

If the virus name begins with Flex or DIO, it is a Cre-dependent virus. Consult the mouse's driver line to determine which cells were labeled with this opsin. Enhancer viruses will deliver their opsin directly to the cell type they target.
# Stimulus

Each experimental session contains an epoch during which laser is presented. We often try to tag two different cell types per mouse: one with a blue opsin, and one with a red opsin. Thus, we present both blue and red laser during the stimulus epoch.

The trial table contains information about each laser presentation that took place, and can be loaded with the following code:

# Identifying tagged neurons

As stated previously, if you know which cell types should be expressing which opsin, you can label units collected during electrophysiology by cell type based on their responses to laser pulses. However, this is not necessarily as straightforward as it might appear: neurons are interconnected and constantly communicating with each other, so changing the activity of one cell will undoubtedly have effects on its neighbors as well. As such, one needs to be very careful in analysing laser responses to make sure you are only considering cells that are directly activated by the laser.

Common metrics for identifying tagged cells include:
* significant increase in firing rate during laser presentation
* low latency of response (as a fast response to the laser rules out synaptic transmission)
* consistency of responses (high percentage of trials with extra spikes)
* low response jitter (one would expect a directly activated cell to have very little variability in when it gets activated)