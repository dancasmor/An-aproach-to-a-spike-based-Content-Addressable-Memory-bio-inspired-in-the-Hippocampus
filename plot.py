
import os
from operator import itemgetter
import matplotlib.pyplot as plt
from excel_controller import ExcelSpikeTracer
import generate_testbench


# Create a folder it it not exist
def create_folder_if_not_exist(path):
    if not os.path.isdir(path):
        os.mkdir(path)


# Plot the spike information
def spikes_plot(spikes, popNames, pointTypes, colors, labels, title, outFilePath, baseFilename, plot, write):
    plt.figure(figsize=(26, 29))
    #plt.figure(figsize=(26, 31))

    # Add point for each neuron of each population that fire, take y labels and x labels
    populationsXValues = []
    populationsYValues = []
    globalIndex = 0
    listYticks = []
    listXticks = []
    for indexPop, populationSpikes in enumerate(spikes):
        xvalues = []
        yvalues = []
        # Assign y value (population index) and y label
        for indexNeuron, spikesSingleNeuron in enumerate(populationSpikes):
            listYticks.append(popNames[indexPop] + str(indexNeuron))
            xvalues = xvalues + spikesSingleNeuron
            yvalues = yvalues + [indexNeuron + globalIndex for i in spikesSingleNeuron]
        globalIndex = globalIndex + len(populationSpikes)
        # Add to the populations values list
        populationsXValues.append(xvalues)
        populationsYValues.append(yvalues)
        # Add xvalues to labels
        listXticks = list(set(listXticks + xvalues))
    maxXvalue = max(listXticks)
    minXvalue = min(listXticks)

    # Lines for each points
    for indexPop in range(len(spikes)):
        plt.vlines(populationsXValues[indexPop], ymin=-1, ymax=populationsYValues[indexPop], color=colors[indexPop],
                   alpha=0.1)
        plt.hlines(populationsYValues[indexPop], xmin=-1, xmax=populationsXValues[indexPop], color=colors[indexPop],
                   alpha=0.1)

    # Add spikes to scatterplot
    for indexPop in range(len(spikes)):
        plt.plot(populationsXValues[indexPop], populationsYValues[indexPop], pointTypes[indexPop],
                 color=colors[indexPop], label=labels[indexPop], markersize=10)

    # Metadata
    plt.xlabel("Simulation time (ms)", fontsize=20)
    plt.ylabel("Neuron spikes", fontsize=20)
    plt.title(title, fontsize=20)
    plt.ylim([-1, globalIndex])
    plt.xlim(-1 + minXvalue, maxXvalue + 1)
    plt.yticks(range(len(listYticks)), listYticks, fontsize=20)
    plt.legend(fontsize=20)


    # Divide xticks list in pair or odd position
    listXticks.sort()
    listXticksOdd = [int(tick) for index, tick in enumerate(listXticks) if not (index % 2 == 0)]
    listXticksPair = [int(tick) for index, tick in enumerate(listXticks) if index % 2 == 0]
    # Write them with alternate distance
    ax = plt.gca()
    ax.set_xticklabels(listXticksOdd, minor=True)
    ax.set_xticks(listXticksOdd, minor=True)
    ax.set_xticklabels(listXticksPair, minor=False)
    ax.set_xticks(listXticksPair, minor=False)
    ax.tick_params(axis='x', which='minor', pad=35)
    ax.tick_params(axis='x', which='both', labelsize=18, rotation=90)

    #plt.legend(fontsize=20, bbox_to_anchor=(1.0, 0.95), loc='upper left')
    #plt.tight_layout()

    # Save and/or plot
    if write:
        # Check if folder exist, if not, create it
        create_folder_if_not_exist(outFilePath)
        plt.savefig(outFilePath + baseFilename + ".png")
    if plot:
        plt.show()


# Format the stream of weight data to a more manageable one: list of {"srcNeuronId", "dstNeuronId", "w", "timeStamp"}
def format_weight_data(weightsDataList, simTime, timeStep):
    srcNeuronId, dstNeuronId, w, timeStampStream = [], [], [], []

    # Generate time steps in ms
    timeStream = [float(t) for t in range(0, simTime +1, int(timeStep))]

    # For each time step:
    for indexStep, step in enumerate(weightsDataList):
        # For each synapse:
        for indexSyn, synapse in enumerate(step):
            srcNeuronId.append(synapse[0])
            dstNeuronId.append(synapse[1])
            w.append(synapse[2])
            timeStampStream.append(timeStream[indexStep])
    return {"srcNeuronId": srcNeuronId, "dstNeuronId": dstNeuronId, "w": w, "timeStep": timeStampStream}


# Create a 3D graph for each postsynaptic neuron ID showing the evolution of the weight of each input synapse
def plot_weight_syn_in_all_neuron(srcNeuronIds, dstNeuronIds, timeStepList, weightsDataList, zlimit, colors, baseFigTitle, figSize, iSplot, iSsave, saveFigName, saveFigPath):
    if iSsave:
        create_folder_if_not_exist(saveFigPath)
    # For each postsynaptic neuron ID
    dstUniqueIds = list(set(dstNeuronIds))
    for dstNeuronId in dstUniqueIds:
        # Extract all postsynaptic neuron ID indeces for the same neuron ID
        dstIndeces = [i for i, value in enumerate(dstNeuronIds) if value == dstNeuronId]
        # Extract the values for the neuron ID, time stamp and weight information of the unique neuronID-value indeces
        srcForSameDst = itemgetter(*dstIndeces)(srcNeuronIds)
        timeForSameDst = itemgetter(*dstIndeces)(timeStepList)
        wForSameDst = itemgetter(*dstIndeces)(weightsDataList)

        # Plot it
        plot_weight_syn_in_single_neuron(x_neuronId=srcForSameDst, y_timestamp=timeForSameDst, z_weight=wForSameDst,
                                         zlimit=zlimit, xlimit=[0, len(list(set(srcNeuronIds)))],
                                         colors=colors, xlabel="Src Neuron", ylabel="Time (ms)", zlabel="Synaptic weight (nA)",
                                         figSize=figSize, figTitle=baseFigTitle + str(dstNeuronId),
                                         iSplot=iSplot, iSsave=iSsave, saveFigName=saveFigName + "_Ni_N" + str(dstNeuronId),
                                         saveFigPath=saveFigPath)


# Plots the evolution of the weight of all input synapses on a postsynaptic neuron (3D figure). For each synapse
#     (x axis) is represented the weight (z axis) in each time stamp (y axis) during the simulation.
def plot_weight_syn_in_single_neuron(x_neuronId, y_timestamp, z_weight, zlimit, xlimit, colors, xlabel, ylabel, zlabel, figSize, figTitle, iSplot, iSsave, saveFigName, saveFigPath):
    fig = plt.figure(figsize=figSize)
    ax = plt.axes(projection="3d")

    # For each unique neuron ID, represent the evolution of weight
    xUniqueValues = list(set(x_neuronId))
    for xUniqueValue in xUniqueValues:
        # Extract all x indeces which have the same x value (for the same neuron ID)
        xIndeces = [i for i, value in enumerate(x_neuronId) if value == xUniqueValue]
        # Extract the values for the neuron ID, time stamp and weight information of the unique neuronID-value indeces
        xForSameX = itemgetter(*xIndeces)(x_neuronId)
        yForSameX = itemgetter(*xIndeces)(y_timestamp)
        zForSameX = itemgetter(*xIndeces)(z_weight)
        ax.plot(xForSameX, yForSameX, zForSameX, color=colors[xUniqueValue], label="Neuron ID " + str(xUniqueValue), alpha=1)

    # Metadata
    ax.set_title(figTitle, fontsize=20)
    ax.set_xlabel(xlabel, fontsize=20)
    ax.set_ylabel(ylabel, fontsize=20)
    ax.set_zlabel(zlabel, fontsize=20)
    ax.set_xticks(xUniqueValues)
    ax.set_zlim3d(zlimit[0], zlimit[1])
    ax.set_xlim3d(xlimit[0], xlimit[1])
    ax.legend(fontsize=20)

    # Save and/or plot the figure
    if iSsave:
        plt.savefig(saveFigPath + saveFigName + ".png")
    if iSplot:
        plt.show()
    plt.close()


def generate_sequence(start, stop, step, divisor):
    # Generate a sequence of numbers with the input conditions (start included, stop not included)
    sequence = []
    count = start
    while count < stop:
        sequence.append(float(count)/divisor)
        count = count + step
    return sequence


def write_file(basePath, filename, extension, data):
    # Generic function to write the data into a file
    file = open(basePath + filename + extension, "w")
    file.write(str(data))
    file.close()
    return basePath + filename + extension, filename


def get_spikes_per_timestamp(spikesInfo, timeStream, cueSize, numContNeuron, fileSavePath="", fileSaveName=""):
    # Order distint streams of spikes by the time stamp when it were fired
    spikesOrderedByTimeStamp = {}

    # Crete a list or reorder indeces for the spikes of INPUT neurons to support endianness codifications
    indexInputSpike = list(range(cueSize)) + list(range(numContNeuron))

    # Check what neurons had fired in each time stamp to store them ordered in the dictionary
    for stamp in timeStream:
        hasSpike = False
        spikesCurrTimeStamp = {}
        # For each population of neuron:
        for spikesInfoSinglePop in spikesInfo.values():
            label = spikesInfoSinglePop["label"]
            spikesCurrTimeStampPopulation_i = []
            spikesCurrTimeStampPopulation_j = [] # Only for IN or OUT population case
            # For each neuron of the current population
            for indexNeuron, spikeStream in enumerate(spikesInfoSinglePop["spikeStream"]):
                # Only if the current neuron has fired in the current time stamp, it is added
                if stamp in spikeStream:
                    if label == "IN" or label == "OUT":
                        # Special case for IN and OUT population: separate IN/OUT cue (True) and IN/OUT cont (False)
                        if indexNeuron < cueSize:
                            spikesCurrTimeStampPopulation_i.append(indexInputSpike[indexNeuron])
                        else:
                            spikesCurrTimeStampPopulation_j.append(indexInputSpike[indexNeuron])
                    else:
                        # Base case
                        spikesCurrTimeStampPopulation_i.append(indexNeuron)
            # Add to the current time stamp the spikes of the current population
            if label == "IN" or label == "OUT":
                spikesCurrTimeStamp[spikesInfoSinglePop["sublabels"][0]] = spikesCurrTimeStampPopulation_i
                spikesCurrTimeStamp[spikesInfoSinglePop["sublabels"][1]] = spikesCurrTimeStampPopulation_j
            else:
                spikesCurrTimeStamp[label] = spikesCurrTimeStampPopulation_i
            # Check if there are spikes in the current time stamp and current population
            hasSpike = hasSpike or spikesCurrTimeStampPopulation_i
            if label == "IN" or label == "OUT":
                hasSpike = hasSpike or spikesCurrTimeStampPopulation_j
        # Add the emptiness of information of the current timestamp
        spikesCurrTimeStamp["hasSpike"] = hasSpike
        # Store all the information using time stamp as a key for the dictionary
        spikesOrderedByTimeStamp.update({stamp: spikesCurrTimeStamp})

    return spikesOrderedByTimeStamp


def get_format_spike_info(spikesInfo, timeStream, cueSize, numContNeuron, allTimeStampInTrace, fileSavePath="", fileSaveName=""):
    # Format all the spikes information along the network to create a readable data structure where the spikes are
    #   ordered by time stamp
    spikesOrderedByTimeStampFormatted = {}

    # Get the spikes ordered by time stamp when they were fired
    spikesOrderedByTimeStamp = get_spikes_per_timestamp(spikesInfo, timeStream, cueSize, numContNeuron,
                                                        fileSavePath=fileSavePath, fileSaveName=fileSaveName)
    indexInputSpike = range(cueSize)

    # Take each time stamp and format the spike information to a more readable one
    for stamp, spikesOrderedInfo in spikesOrderedByTimeStamp.items():
        hasSpike = False
        # For each population in the current time stamp:
        spikesCurrTimeStamp = {}
        for label, spikeStream in spikesOrderedInfo.items():
            formatSpikes = None
            if label == "hasSpike":
                # spikeStream denote if there is any spike in the current time stamp
                hasSpike = spikeStream
                continue
            elif spikeStream:
                # Base format information: dont do anything, pass as is
                formatSpikes = spikeStream
            else:
                continue
            spikesCurrTimeStamp[label] = formatSpikes
        # Only take time stamp if there are spikes
        if allTimeStampInTrace or hasSpike:
            spikesOrderedByTimeStampFormatted.update({stamp: spikesCurrTimeStamp})
    return spikesOrderedByTimeStampFormatted


def get_string_format_spike_info_each_timestamp(spikes, numContNeuron):
    # Given spike information of neurons at a specific time stamp, format it to a more friendly-redable format

    # + Reformat spike information to string
    # + Change False and [] values for - char to indicate that there is no relevant information

    # INcue
    inCue = str(spikes["INcue"]) if ("INcue" in spikes) and not (spikes["INcue"] == []) and (
            spikes["INcue"] is not False) else "-"

    # INcont
    inCont = str(spikes["INcont"]) if ("INcont" in spikes) and not (spikes["INcont"] == []) and (
            spikes["INcont"] is not False) else "-"

    # CueCue
    cueCue = str(spikes["CueCue"]) if ("CueCue" in spikes) and not (spikes["CueCue"] == []) and (
            spikes["CueCue"] is not False) else "-"

    # ContCue
    contCue = str(spikes["ContCue"]) if ("ContCue" in spikes) and not (spikes["ContCue"] == []) and (
            spikes["ContCue"] is not False) else "-"

    # CueCont
    cueCont = str(spikes["CueCont"]) if ("CueCont" in spikes) and not (spikes["CueCont"] == []) and (
            spikes["CueCont"] is not False) else "-"

    # ContCont
    contCont = str(spikes["ContCont"]) if ("ContCont" in spikes) and not (spikes["ContCont"] == []) and (
            spikes["ContCont"] is not False) else "-"

    # ContCond
    contCond = str(spikes["ContCond"]) if ("ContCond" in spikes) and not (spikes["ContCond"] == []) and (
            spikes["ContCond"] is not False) else "-"

    # ContCondInt
    contCondInt = str(spikes["ContCondInt"]) if ("ContCondInt" in spikes) and not (spikes["ContCondInt"] == []) and (
            spikes["ContCondInt"] is not False) else "-"

    # MergeCue
    mergeCue = str(spikes["MergeCue"]) if ("MergeCue" in spikes) and not (spikes["MergeCue"] == []) and (
            spikes["MergeCue"] is not False) else "-"

    # MerceCont
    merceCont = str(spikes["MergeCont"]) if ("MergeCont" in spikes) and not (spikes["MergeCont"] == []) and (
            spikes["MergeCont"] is not False) else "-"

    # OUTcue
    outCue = str(spikes["OUTcue"]) if ("OUTcue" in spikes) and not (spikes["OUTcue"] == []) and (
            spikes["OUTcue"] is not False) else "-"

    # OUTcont: represent the content of memories in binary and in neurons activated
    outCont = str(spikes["OUTcont"]) if ("OUTcont" in spikes) and not (spikes["OUTcont"] == []) and (
            spikes["OUTcont"] is not False) else "-"

    return [inCue, inCont, cueCue, contCue, cueCont, contCont, contCond, contCondInt, mergeCue, merceCont,
            outCue, outCont]


def generate_table_excel(spikesInfo, timeStream, numCueOneHotNeuron, numContNeuron, allTimeStampInTrace, fileSavePath,
                         fileSaveName, simTime, colors, orientationFormat, headers, boxTableSize):
    # Create an excel table with all spike information formatted
    # Check if folder path exist and create in other case
    generate_testbench.check_and_create_folder(fileSavePath)

    # Get the spikes ordered by time stamp when they were fired and formatted to a more readable style
    spikesOrderedByTimeStampFormatted = get_format_spike_info(spikesInfo, timeStream, numCueOneHotNeuron,
                                                              numContNeuron, allTimeStampInTrace,
                                                              fileSavePath=fileSavePath, fileSaveName=fileSaveName)

    # Create matrix of information whose rows is the spike information formatted at a specific time stamp and
    #  columns represent the values for a specific population of neuron along the simulation time
    matrixSpikeInfo = []
    for stamp, spikes in spikesOrderedByTimeStampFormatted.items():
        [inCue, inContBin, cueCue, contCue, cueCont, contCont, contCond, contCondInt, mergeCue, merceCont,
         outCue, outContBin] = get_string_format_spike_info_each_timestamp(spikes, numContNeuron)

        matrixSpikeInfo.append([inCue, inContBin, cueCue, contCue, contCond, contCondInt, cueCont, contCont, mergeCue,
                                merceCont, outCue, outContBin])

    # Excel file creation
    excelFile = ExcelSpikeTracer(fileSavePath, fileSaveName, simTime, len(matrixSpikeInfo[0]), colors["bgColor"],
                                 colors["hdColor"], orientationFormat, boxTableSize)

    # Add the headers to the excel table depend on the orientation
    if orientationFormat == "horizontal":
        excelFile.print_column(0, True, headers, colors["hdColor"])
    else:
        excelFile.print_row(0, True, headers, colors["hdColor"])

    # Add the format spike information to the excel table depend on the orientation
    indexCount = 1
    cellColor = [colors["IN"], colors["IN"], colors["CA3cue"], colors["CA3cue"], colors["INT"], colors["INT"],
                 colors["CA3cont"], colors["CA3cont"], colors["MERGE"], colors["MERGE"], colors["OUT"], colors["OUT"]]
    for spikePop in matrixSpikeInfo:
        if orientationFormat == "horizontal":
            excelFile.print_column(indexCount, False, spikePop, cellColor)
        else:
            excelFile.print_row(indexCount, False, spikePop, cellColor)
        indexCount = indexCount + 1

    # Close and save file
    excelFile.closeExcel()
    return excelFile.fullPath