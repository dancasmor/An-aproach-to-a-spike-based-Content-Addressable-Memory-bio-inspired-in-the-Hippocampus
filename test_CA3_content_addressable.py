
from CA3_content_addressable import Memory
import spynnaker8 as sim
import plot
import json


# Parameters:
# + Number of directions of the memory
cueSize = 5
# + Size of the content of the memory in bits/neuron
contSize = 10

# + Time step of the simulation
timeStep = 1.0

# + Experiment:
experiment = 1
#   TEST:
#   1) Mix of learn, recall by cue, recall by cont, learn with forget and recall by cue and cont again (10 ms each op)
#   2) TB2 -> piramidal sequence: learn for each cue the cue as content, recall by cue and recall by content for all neurons,
#               and the same but with complemented content 2 times
#   3) Flag based state maps: a 4x4 grid map of the environment is available. Each memory cue represents a cell on
#       the map and the content of the memory represents for each neuron a possible state (flags).
#      For this application, we are going to assume that a spiking robotic system travels through the environment and
#       provides its state information to the memory. Therefore, in the first half of the simulation,
#       the map of states in memory will be introduced. This map will have a total of 6 biologically plausible
#       states: unknown (neuron 0), initial position (neuron 1), goal position (neuron 2), free (neuron 3),
#       path (neuron 4) and obstacle (neuron 5).
#      In the second half of the simulation, the desired functionality of this application is provided. Obtain which
#      specific cells of the map have at least one of the different states of interest in a single read/recall
#      operation. Specifically, it would be information of interest to know:
#           + The sequence of cells that the robot travels through to get from the origin to the target
#              (initial position, target and path states).
#           + The set of cells that are free to trace new possible paths.
#           + The set of cells with obstacles to know the topology of the environment.
#           + the set of cells of unknown status to be explored in future incursions.

if experiment == 1:
    # op -> t=0[0]=[0,1,8,9], t=10[4]=[1,5,6], t=20[3]=[4,5,6,8], t=30[0], t=40[]=[6], t=50[]=[0,4],
    #       t=60[3]=[1,3,4,8], t=70[3], t=80[]=[6]
    # + Spikes of the input layer
    inputSpikesCue = [[0, 1, 2, 30], [], [], [20, 21, 22, 60, 61, 62, 70], [10, 11, 12]]
    inputSpikesCont = [[0, 1, 2, 50], [0, 1, 2, 10, 11, 12, 60, 61, 62], [], [60, 61, 62], [20, 21, 22, 50, 60, 61, 62],
                       [10, 11, 12, 20, 21, 22], [10, 11, 12, 20, 21, 22, 40, 80], [], [0, 1, 2, 60, 61, 62], [0, 1, 2]]
    # + Duration of the simulation
    simTime = 90
    # + Name of the experiment, i.e., name of the generated figure
    experiment_name = "1_learn_recall_by_cue_and_cont_forget"
    # + If record the STDP synapses in order to get a evolution of the weight of that synapses along the simulation
    recordWeight = False
elif experiment == 2:
    # Write all directions from 0 to cueSize-1, read all by cue and by cont
    inputInfo = json.load(open("tb/tb2_piramidal_cont/input_spikes.txt"))
    inputSpikesCue = inputInfo["cue"]
    inputSpikesCont = inputInfo["cont"]
    simTime = inputInfo["simTime"]
    experiment_name = "2_tb2_piramidal_sequence_cont"
    recordWeight = False
elif experiment == 3:
    # This experiment has different memory size: 16 cue, one for each cell of the map, and 6 content neuron, one for
    #  each possible state
    cueSize = 16
    contSize = 6
    # The map will hace the following state:
    #   0 5 1 3
    #   0 3 4 5
    #   0 5 4 3
    #   2 4 4 3
    inputSpikesCue = [[0,1,2], [7,8,9], [14,15,16], [21,22,23],
                      [28,29,30], [35,36,37], [42,43,44], [49,50,51],
                      [56,57,58], [63,64,65], [70,71,72], [77,78,79],
                      [84,85,86], [91,92,93], [98,99,100], [105,106,107]]
    inputSpikesCont = [[0,1,2, 28,29,30, 56,57,58, 130],
                       [14,15,16, 112],
                       [84,85,86, 112],
                       [21,22,23, 35,36,37, 77,78,79, 105,106,107, 118],
                       [42,43,44, 70,71,72, 91,92,93, 98,99,100, 112],
                       [7,8,9, 49,50,51, 63,64,65, 124]]
    simTime = 140
    experiment_name = "3_state_map_app"
    recordWeight = False

else:
    inputSpikesCue = [[], [], [], [], []]
    inputSpikesCont = [[], [], [], [], [], [], [], [], [], []]
    simTime = 1
    experiment_name = "none"
    recordWeight = False
inputSpikes = inputSpikesCue + inputSpikesCont


def test():
    # + Number of neurons in input layer: the number of bits neccesary to represent the number of directions
    #       in binary + the size of patterns
    numInputLayerNeurons = cueSize + contSize

    # Setup simulation
    sim.setup(timeStep)

    # Create network
    # Input layer
    ILayer = sim.Population(numInputLayerNeurons, sim.SpikeSourceArray(spike_times=inputSpikes), label="ILayer")
    # Output layer: fire a spike when receive a spike
    neuronParameters = {"cm": 0.27, "i_offset": 0.0, "tau_m": 3.0, "tau_refrac": 1.0, "tau_syn_E": 0.3, "tau_syn_I": 0.3,
                        "v_reset": -60.0, "v_rest": -60.0, "v_thresh": -57.5}
    OLayer = sim.Population(numInputLayerNeurons, sim.IF_curr_exp(**neuronParameters), label="OLayer")
    OLayer.set(v=-60)
    # Create memory
    memory = Memory(cueSize, contSize, sim)
    memory.connect_in(ILayer)
    memory.connect_out(OLayer)

    # Record spikes from output layer
    memory.CA3cueCueRecallLayer.record(["spikes"])
    memory.CA3cueContRecallLayer.record(["spikes"])
    memory.CA3contCueRecallLayer.record(["spikes"])
    memory.CA3contContRecallLayer.record(["spikes"])
    memory.CA3contCondLayer.record(["spikes"])
    memory.CA3contCondIntLayer.record(["spikes"])
    memory.CA3mergeCueLayer.record(["spikes"])
    memory.CA3mergeContLayer.record(["spikes"])
    OLayer.record(["spikes"])

    # Begin simulation
    if recordWeight:
        w_CA3cueL_CA3contL = []
        w_CA3contL_CA3cueL = []
        w_CA3cueL_CA3contL.append(memory.CA3cueCueRecallL_CA3contCueRecallL_conn.get('weight', format='list', with_address=True))  # t=0
        w_CA3contL_CA3cueL.append(memory.CA3contContRecallL_CA3cueContRecallL_conn.get('weight', format='list', with_address=True))  # t=0
        for n in range(0, int(simTime), int(timeStep)):
            sim.run(timeStep)
            w_CA3cueL_CA3contL.append(memory.CA3cueCueRecallL_CA3contCueRecallL_conn.get('weight', format='list', with_address=True))
            w_CA3contL_CA3cueL.append(memory.CA3contContRecallL_CA3cueContRecallL_conn.get('weight', format='list', with_address=True))
    else:
        sim.run(simTime)

    # Get spike information
    #   - CA3cueCueRecallLayer
    spikes = memory.CA3cueCueRecallLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    formatSpikesCA3cueCueRecallLayer = []
    for neuron in spikes:
        formatSpikesCA3cueCueRecallLayer.append(neuron.as_array().tolist())
    #   - CA3cueContRecallLayer
    spikes = memory.CA3cueContRecallLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    formatSpikesCA3cueContRecallLayer = []
    for neuron in spikes:
        formatSpikesCA3cueContRecallLayer.append(neuron.as_array().tolist())
    #   - CA3contCueRecallLayer
    spikes = memory.CA3contCueRecallLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    formatSpikesCA3contCueRecallLayer = []
    for neuron in spikes:
        formatSpikesCA3contCueRecallLayer.append(neuron.as_array().tolist())
    #   - CA3contCond
    spikes = memory.CA3contCondLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    formatSpikesCA3contCondLayer = []
    for neuron in spikes:
        formatSpikesCA3contCondLayer.append(neuron.as_array().tolist())
    #   - CA3contCondInt
    spikes = memory.CA3contCondIntLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    formatSpikesCA3contCondIntLayer = []
    for neuron in spikes:
        formatSpikesCA3contCondIntLayer.append(neuron.as_array().tolist())
    #   - CA3contContRecallLayer
    spikes = memory.CA3contContRecallLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    formatSpikesCA3contContRecallLayer = []
    for neuron in spikes:
        formatSpikesCA3contContRecallLayer.append(neuron.as_array().tolist())
    #   - CA3mergeCueLayer
    spikes = memory.CA3mergeCueLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    formatSpikesCA3mergeCueLayer= []
    for neuron in spikes:
        formatSpikesCA3mergeCueLayer.append(neuron.as_array().tolist())
    #   - CA3mergeContLayer
    spikes = memory.CA3mergeContLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    formatSpikesCA3mergeContLayer = []
    for neuron in spikes:
        formatSpikesCA3mergeContLayer.append(neuron.as_array().tolist())
    #   - OUT
    spikes = OLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    formatSpikesOut = []
    for neuron in spikes:
        formatSpikesOut.append(neuron.as_array().tolist())

    # End simulation
    sim.end()

    # Plot results
    #   + Check if results folder exist, if not, create it
    plot.create_folder_if_not_exist("results/")
    #   + Spike activities plot
    plot.spikes_plot([inputSpikes, formatSpikesCA3cueCueRecallLayer, formatSpikesCA3contCueRecallLayer,
                      formatSpikesCA3contCondLayer, formatSpikesCA3contCondIntLayer,
                      formatSpikesCA3cueContRecallLayer, formatSpikesCA3contContRecallLayer,
                      formatSpikesCA3mergeCueLayer, formatSpikesCA3mergeContLayer, formatSpikesOut],
                     ["IN", "CueCue", "ContCue", "ContCond", "ContCondInt", "CueCont", "ContCont", "MergeCue", "MergeCont", "OUT"],
                     ["o", "o", "o", "o", "o", "o", "o", "o", "o", "o"],
                     ["green", "orange", "gold", "black", "navy", "teal", "aqua", "darkviolet", "blue", "red"],
                     ["IN", "CA3cueCueRecall", "CA3contCueRecall", "CA3contCond", "CA3contCondInt", "CA3cueContRecall",
                      "CA3contContRecall", "CA3MergeCue", "CA3MergeCont", "OUT"],
                     "Hipocampal spikes", "results/"+experiment_name+"/", "spikes", False, True)
    #   + Spike activities in excell
    timeStream = plot.generate_sequence(0, simTime, timeStep, 1)
    spikesInfo = {}
    spikesInfo["IN"] = {"spikeStream": inputSpikes, "label": "IN", "sublabels": ["INcue", "INcont"], "color": "green"}
    spikesInfo["CueCue"] = {"spikeStream": formatSpikesCA3cueCueRecallLayer, "label": "CueCue", "sublabels": ["CueCue"], "color": "orange"}
    spikesInfo["ContCue"] = {"spikeStream": formatSpikesCA3contCueRecallLayer, "label": "ContCue", "sublabels": ["ContCue"], "color": "gold"}
    spikesInfo["ContCond"] = {"spikeStream": formatSpikesCA3contCondLayer, "label": "ContCond", "sublabels": ["ContCond"], "color": "black"}
    spikesInfo["ContCondInt"] = {"spikeStream": formatSpikesCA3contCondIntLayer, "label": "ContCondInt", "sublabels": ["ContCondInt"],
                             "color": "navy"}
    spikesInfo["CueCont"] = {"spikeStream": formatSpikesCA3cueContRecallLayer, "label": "CueCont", "sublabels": ["CueCont"], "color": "teal"}
    spikesInfo["ContCont"] = {"spikeStream": formatSpikesCA3contContRecallLayer, "label": "ContCont", "sublabels": ["ContCont"], "color": "aqua"}
    spikesInfo["MergeCue"] = {"spikeStream": formatSpikesCA3mergeCueLayer, "label": "MergeCue", "sublabels": ["MergeCue"], "color": "darkviolet"}
    spikesInfo["MergeCont"] = {"spikeStream": formatSpikesCA3mergeContLayer, "label": "MergeCont", "sublabels": ["MergeCont"], "color": "blue"}
    spikesInfo["OUT"] = {"spikeStream": formatSpikesOut, "label": "OUT", "sublabels": ["OUTcue", "OUTcont"], "color": "red"}
    excelColors = {"bgColor": "#FCE4D6", "hdColor": "#F4B084", "IN": "#8DB4E2", "CA3cue": "#FFF2CC", "CA3cont": "#ABEBC6",
                   "OUT": "#FFC000", "INT": "#D2B4DE", "MERGE": "#85929E"}
    plot.generate_table_excel(spikesInfo=spikesInfo, timeStream=timeStream,
                              numCueOneHotNeuron=cueSize, numContNeuron=contSize, allTimeStampInTrace=True,
                              fileSavePath="results/"+experiment_name+"/", fileSaveName="spikes", simTime=simTime,
                              colors=excelColors, orientationFormat="vertical",
                              headers=["TimeStamp (ms)", "INcue", "INcont", "CA3cueCueRecall", "CA3contCueRecall",
                                       "CA3contCond", "CA3contCondInt", "CA3cueContRecall", "CA3contContRecall",
                                       "CA3MergeCue", "CA3MergeCont", "OUTcue", "OUTcont"],
                              boxTableSize=25)
    #   + Weight of STDP synapses
    if recordWeight:
        # Format data
        formatWeightCA3cueL_CA3contL = plot.format_weight_data(w_CA3cueL_CA3contL, simTime, timeStep)
        formatWeightCA3contL_CA3cueL = plot.format_weight_data(w_CA3contL_CA3cueL, simTime, timeStep)
        # Generate as many colors as number of CA3cue neurons and CA3cont neurons
        colorsCue = ["#da0605", "#4b1d73", "#7d2702", "#26e223", "#1f02d6"]
        colorsCont = ["#417155", "#A35C61", "#2057EB", "#663ED1", "#1B2850", "#D0D714", "#1299EE", "#0EB9A3", "#81B684", "#F984C7"]
        # Plot
        plot.plot_weight_syn_in_all_neuron(srcNeuronIds=formatWeightCA3cueL_CA3contL["srcNeuronId"],
                                           dstNeuronIds=formatWeightCA3cueL_CA3contL["dstNeuronId"],
                                           timeStepList=formatWeightCA3cueL_CA3contL["timeStep"],
                                           weightsDataList=formatWeightCA3cueL_CA3contL["w"],
                                           zlimit=[memory.synParameters["CA3cueCueRecallL-CA3contCueRecallL"]["w_min"] - 0.5,
                                                   memory.synParameters["CA3cueCueRecallL-CA3contCueRecallL"]["w_max"] - 0.5],
                                           colors=colorsCue, baseFigTitle="Weight CA3cue_i-CA3cont_", figSize=(20, 16),
                                           iSplot=False, iSsave=True,
                                           saveFigName="ca3cue_ca3cont_w",
                                           saveFigPath="results/" + experiment_name + "/ca3cue_ca3cont/")
        plot.plot_weight_syn_in_all_neuron(srcNeuronIds=formatWeightCA3contL_CA3cueL["srcNeuronId"],
                                           dstNeuronIds=formatWeightCA3contL_CA3cueL["dstNeuronId"],
                                           timeStepList=formatWeightCA3contL_CA3cueL["timeStep"],
                                           weightsDataList=formatWeightCA3contL_CA3cueL["w"],
                                           zlimit=[memory.synParameters["CA3contContRecallL-CA3cueContRecallL"]["w_min"] - 0.5,
                                                   memory.synParameters["CA3contContRecallL-CA3cueContRecallL"]["w_max"] - 0.5],
                                           colors=colorsCont, baseFigTitle="Weight CA3cont_i-CA3cue_", figSize=(20, 16),
                                           iSplot=False, iSsave=True,
                                           saveFigName="ca3cont_ca3cue_w",
                                           saveFigPath="results/" + experiment_name + "/ca3cont_ca3cue/")

    print("Finished!")


if __name__ == "__main__":
    test()
