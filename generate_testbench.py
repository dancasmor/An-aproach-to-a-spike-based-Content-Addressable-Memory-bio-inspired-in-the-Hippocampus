import numpy as np
import os

# + Number of directions of the memory
cueSize = 5
# + Size of the content of the memory in bits/neuron
contSize = 10
# + Time step of the simulation
timeStep = 1.0
# + Time after operations
#   - 14 ms after learning
learnOperationTime = 14
#   - 14 ms after recall
recallOperationTime = 14


# TOOLS ----------------------------------------------------------------

def check_and_create_folder(path):
    # Check if a folder exist and, if it does not exist, it creates it
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
            return path
        except OSError as e:
            print("Error to create directory")
            return False
    else:
        return path


def write_file(basePath, filename, extension, data):
    # Generic function to write the data into a file
    file = open(basePath + filename + extension, "w")
    file.write(str(data))
    file.close()
    return basePath + filename + extension, filename


def decimal_to_binary(num, list):
    # Convert a decimal number to a list of the binary values
    if num >= 1:
        decimal_to_binary(num // 2, list)
    list.append(num % 2)


def decimal_to_binary_list(decimalList):
    # Convert a list of decimal numbers to a list of binary numbers, each binary value is a list of 0's and 1's
    # Create the list of cues in binary
    binaryValues = [[] for i in range(len(decimalList))]
    for index, value in enumerate(decimalList):
        # Get the binary representation of the current cue
        decimal_to_binary(value, binaryValues[index])
    return binaryValues


def complement_binary_list(binaryList):
    # Complement all values in binary list
    complementList = [[] for i in range(len(binaryList))]
    for indexNeuron, binValues in enumerate(binaryList):
        for value in binValues:
            if value == 1:
                complementList[indexNeuron].append(0)
            else:
                complementList[indexNeuron].append(1)
    return complementList


def format_cue_vectors(binaryCueValues, cueSize):
    # Format the input list of binary values to have the same size of numbers of neuron in the input cue population
    for index in range(len(binaryCueValues)):
        # Fix it to have cueSizeInBin binary numbers
        if len(binaryCueValues[index]) < cueSize:
            # If it has less values, fill with 0's at the begining
            binaryCueValues[index] = [0] * (cueSize - len(binaryCueValues[index])) + binaryCueValues[index]
        elif len(binaryCueValues[index]) > cueSize:
            binaryCueValues[index] = binaryCueValues[index][len(binaryCueValues[index]) - cueSize:]
    return binaryCueValues


def create_cue_input_vector(cue, cueValues, currentOperationTime, operationTime, holdingTime, numOperations):
    # Associate each cue value to input operations
    for indexCue, value in enumerate(cueValues):
        # Hold the values as time as the operation need
        for holdingIndex in range(holdingTime):
            cue[value].append(currentOperationTime + holdingIndex)
        # Add to the current operation time the minimum time to begin the next operation
        currentOperationTime = currentOperationTime + operationTime
        numOperations = numOperations + 1
    return cue, numOperations, currentOperationTime


def create_cont_input_vector(cont, contBinValues, currentOperationTime, operationTime, holdingTime):
    # Take a list of binary values to assign them to the correct content neuron in the correct time stamp to do the operation
    # Associate each binary value of each cue as an activation of a neuron input
    for indexCont, contBinValue in enumerate(contBinValues):
        for indexValue, binaryValue in enumerate(contBinValue):
            # Only put "active" values (1 in binary)
            if binaryValue == 1:
                # Hold the values as time as the operation need
                for holdingIndex in range(holdingTime):
                    cont[indexValue].append(currentOperationTime + holdingIndex)
        # Add to the current operation time the minimum time to begin the next operation
        currentOperationTime = currentOperationTime + operationTime
    return cont, currentOperationTime


def create_alternate_cue_input_vector(cue, binaryCueValues, currentOperationTime, operationTime, holdingTime, numOperations):
    # Take a list of binary values to assign them to the correct cue neuron in the correct time stamp to do the
    #  operation adding 2 times the value once for writing and once for reading it

    # Associate each binary value of each cue as an activation of a neuron input
    for indexCue, inputBinaryCue in enumerate(binaryCueValues):
        # + For the writing operation
        for indexValue, binaryValue in enumerate(inputBinaryCue):
            # Only put "active" values (1 in binary)
            if binaryValue == 1:
                # Hold the values as time as the operation need
                for holdingIndex in range(holdingTime[0]):
                    cue[indexValue].append(currentOperationTime + holdingIndex)
        # Add to the current operation time the minimum time to begin the next operation
        currentOperationTime = currentOperationTime + operationTime[0]
        numOperations = numOperations + 1
        # + For the reading operation
        for indexValue, binaryValue in enumerate(inputBinaryCue):
            # Only put "active" values (1 in binary)
            if binaryValue == 1:
                # Hold the values as time as the operation need
                for holdingIndex in range(holdingTime[1]):
                    cue[indexValue].append(currentOperationTime + holdingIndex)
        currentOperationTime = currentOperationTime + operationTime[1]
        numOperations = numOperations + 1
    return cue, numOperations, currentOperationTime


# TESTBENCHS ----------------------------------------------------------------

def tb_piramidal_sequence():
    # Testbench 1 -> piramidal sequence
    ## 1) Writing all cues as cont
    #   * Create the empty cue vector
    cue = [[] for i in range(cueSize)]
    #   * Create the list of cues
    cueValues = [i for i in range(cueSize)]
    #   * Assign the values to each input cue neuron on the correct timestamp (assign operation)
    currentOperationTime = 1
    numOperations = 0
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       learnOperationTime, 3, numOperations)

    # + Create the input cont activity vector
    #   * Create the empty cont vector
    cont = [[] for i in range(contSize)]
    #   * Create the list of content in decimal
    numOperationsCont = numOperations
    decimalCont = [(i + 1) % (2 ** contSize) for i in range(numOperationsCont)]
    #   * Convert the cont from decimal to binary and fix it to the correct input size
    binaryCont = format_cue_vectors(decimal_to_binary_list(decimalCont), contSize)
    #   * Generate the data to store
    currentOperationTimeCont = 1
    cont, currentOperationTime = create_cont_input_vector(cont, binaryCont, currentOperationTimeCont,
                                                          learnOperationTime, 3)

    ## 2) Reading all cues
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       recallOperationTime, 1, numOperations)

    ## 3) Write the complementary of the current content
    #   * Cue
    currentOperationTimeCont = currentOperationTime
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       learnOperationTime, 3, numOperations)
    #   * Content (complemented)
    binaryCont = complement_binary_list(binaryCont)
    cont, currentOperationTime = create_cont_input_vector(cont, binaryCont, currentOperationTimeCont,
                                                          learnOperationTime, 3)

    ## 4) Read all cues
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       recallOperationTime, 1, numOperations)

    ## 5) Write the complementary of the current content
    #   * Cue
    currentOperationTimeCont = currentOperationTime
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       learnOperationTime, 3, numOperations)
    #   * Content (complemented)
    binaryCont = complement_binary_list(binaryCont)
    cont, currentOperationTime = create_cont_input_vector(cont, binaryCont, currentOperationTimeCont,
                                                          learnOperationTime, 3)

    ## 6) Read all cues
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       recallOperationTime, 1, numOperations)

    return cue, cont, currentOperationTime, numOperations


def tb_piramidal_sequence_content_addresable():
    # Testbench 1 -> piramidal sequence
    ## 1) Writing all cues as cont
    #   * Create the empty cue vector
    cue = [[] for i in range(cueSize)]
    #   * Create the list of cues
    cueValues = [i for i in range(cueSize)]
    #   * Assign the values to each input cue neuron on the correct timestamp (assign operation)
    currentOperationTime = 1
    numOperations = 0
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       learnOperationTime, 3, numOperations)

    # + Create the input cont activity vector
    #   * Create the empty cont vector
    cont = [[] for i in range(contSize)]
    #   * Create the list of content in decimal
    numOperationsCont = numOperations
    decimalCont = [(i + 1) % (2 ** contSize) for i in range(numOperationsCont)]
    #   * Convert the cont from decimal to binary and fix it to the correct input size
    binaryCont = format_cue_vectors(decimal_to_binary_list(decimalCont), contSize)
    #   * Generate the data to store
    currentOperationTimeCont = 1
    cont, currentOperationTime = create_cont_input_vector(cont, binaryCont, currentOperationTimeCont,
                                                          learnOperationTime, 3)

    ## 2) Reading all cues
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       recallOperationTime, 1, numOperations)

    ## 3) Reading all cont
    contDecimal = [i for i in range(contSize)]
    contDecimal.reverse()
    cont, numOperations, currentOperationTime = create_cue_input_vector(cont, contDecimal, currentOperationTime,
                                                                       recallOperationTime, 1, numOperations)

    ## 4) Write the complementary of the current content
    #   * Cue
    currentOperationTimeCont = currentOperationTime
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       learnOperationTime, 3, numOperations)
    #   * Content (complemented)
    binaryCont = complement_binary_list(binaryCont)
    cont, currentOperationTime = create_cont_input_vector(cont, binaryCont, currentOperationTimeCont,
                                                          learnOperationTime, 3)

    ## 5) Read all cues
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       recallOperationTime, 1, numOperations)

    ## 6) Reading all cont
    cont, numOperations, currentOperationTime = create_cue_input_vector(cont, contDecimal, currentOperationTime,
                                                                        recallOperationTime, 1, numOperations)

    ## 7) Write the complementary of the current content
    #   * Cue
    currentOperationTimeCont = currentOperationTime
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       learnOperationTime, 3, numOperations)
    #   * Content (complemented)
    binaryCont = complement_binary_list(binaryCont)
    cont, currentOperationTime = create_cont_input_vector(cont, binaryCont, currentOperationTimeCont,
                                                          learnOperationTime, 3)

    ## 8) Read all cues
    cue, numOperations, currentOperationTime = create_cue_input_vector(cue, cueValues, currentOperationTime,
                                                                       recallOperationTime, 1, numOperations)

    ## 9) Reading all cont
    cont, numOperations, currentOperationTime = create_cue_input_vector(cont, contDecimal, currentOperationTime,
                                                                        recallOperationTime, 1, numOperations)

    return cue, cont, currentOperationTime, numOperations


def generate_testbench():
    # Create the directory to store the tb if it isn't exist
    check_and_create_folder("tb/")

    # Testbench 1 -> piramidal sequence
    tb1_cue, tb1_cont, tb1_currentOperationTime, tb1_numOperations = tb_piramidal_sequence()
    tb1_cont.reverse()
    # Store it
    print("Testbench 1: piramidal sequence")
    print("Min simulation time to simulate all operations = " + str(tb1_currentOperationTime) + " ms")
    print("Num of operations = " + str(tb1_numOperations))
    # Write the results
    tb_data = "{\"simTime\": " + str(tb1_currentOperationTime+10) + " , \"numOperations\": " + str(tb1_numOperations) \
              + ", \"cue\":" + str(tb1_cue) + ", \"cont\":" + str(tb1_cont) + "}"
    tbFullPath = check_and_create_folder("tb/tb1_piramidal/")
    path, filename = write_file(tbFullPath, "input_spikes", ".txt", tb_data)
    print(path + "\n\n")

    # Testbench 2 -> piramidal sequence content addresable
    tb2_cue, tb2_cont, tb2_currentOperationTime, tb2_numOperations = tb_piramidal_sequence_content_addresable()
    tb2_cont.reverse()
    # Store it
    print("Testbench 2: piramidal sequence content addresable")
    print("Min simulation time to simulate all operations = " + str(tb2_currentOperationTime) + " ms")
    print("Num of operations = " + str(tb2_numOperations))
    # Write the results
    tb_data = "{\"simTime\": " + str(tb2_currentOperationTime + 10) + " , \"numOperations\": " + str(tb2_numOperations) \
              + ", \"cue\":" + str(tb2_cue) + ", \"cont\":" + str(tb2_cont) + "}"
    tbFullPath = check_and_create_folder("tb/tb2_piramidal_cont/")
    path, filename = write_file(tbFullPath, "input_spikes", ".txt", tb_data)
    print(path + "\n\n")


if __name__ == "__main__":
    generate_testbench()