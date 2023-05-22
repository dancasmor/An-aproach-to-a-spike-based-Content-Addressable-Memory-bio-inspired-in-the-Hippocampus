# Bio-inspired computational memory model of the Hippocampus: an aproach to a spike-based Content-Addressable Memory

<h2 name="Description">Description</h2>
<p align="justify">
Code on which the paper entitled "Bio-inspired computational memory model of the Hippocampus: an aproach to a spike-based Content-Addressable Memory" is based, sent to a journal and awaiting review.
</p>
<p align="justify">
A fully functional spike-based Content-Addressable Memory model bio-inspired in the CA3 region of the hippocampus implemented on the <a href="https://apt.cs.manchester.ac.uk/projects/SpiNNaker/">SpiNNaker</a> hardware platform using the technology of the Spiking Neuronal Network (SNN) is presented. The code is written in Python and makes use of the PyNN library and their adaptation for SpiNNaker called <a href="https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjaxOCWhrn3AhVL1BoKHVtQDvsQFnoECAkQAQ&url=https%3A%2F%2Fgithub.com%2FSpiNNakerManchester%2FsPyNNaker&usg=AOvVaw3e3TBMJ-08yBqtsKza_RiE">sPyNNaker</a>. In addition, the necessary scripts to replicate the tests and plots carried out in the paper are included, together with data and plots of the tests.
</p>
<p align="justify">
Please go to section <a href="#CiteThisWork">cite this work</a> to learn how to properly reference the works cited here.
</p>


<h2>Table of contents</h2>
<p align="justify">
<ul>
<li><a href="#Description">Description</a></li>
<li><a href="#Article">Article</a></li>
<li><a href="#Instalation">Instalation</a></li>
<li><a href="#Usage">Usage</a></li>
<li><a href="#RepositoryContent">Repository content</a></li>
<li><a href="#CiteThisWork">Cite this work</a></li>
<li><a href="#Credits">Credits</a></li>
<li><a href="#License">License</a></li>
</ul>
</p>


<h2 name="Article">Article</h2>
<p align="justify">
<strong>Title</strong>: Bio-inspired computational memory model of the Hippocampus: an aproach to a spike-based Content-Addressable Memory

<strong>Abstract</strong>: The brain has computational capabilities that surpass those of modern systems, being able to solve complex problems efficiently in a simple way. Neuromorphic engineering tries to mimic biology in order to develop new systems capable of incorporating such capabilities. Bio-inspired learning systems still remain as a challenge to be solved and with much work yet to be done. Among all brain regions, the hippocampus stands out as an autoassociative short-term memory with the capacity to learn and recall memories from any fragment of them. These characteristics make the hippocampus an ideal candidate as a material for developing bio-inspired learning systems that, in addition, resemble content-addressable memories. Therefore, in this work we propose a bio-inspired spiking content-addressable memory model based in the CA3 region of the hippocampus with the ability to learn, forget and recall memories, both orthogonal and non-orthogonal, from any fragment of them. The model was implemented on the SpiNNaker hardware platform using Spiking Neural Networks. A set of experiments based on functional, stress and applicability tests were performed to demonstrate its correct functioning. This work presents the first hardware implementation of a fully-functional bio-inspired spiking hippocampal content-addressable memory model, paving the way for the development of future more complex neuromorphic systems.

<strong>Keywords</strong>: Hippocampus model, Content-Addressable memory, Spiking Neural Networks, Neuromorphic engineering, CA3, SpiNNaker

<strong>Author</strong>: Daniel Casanueva-Morato

<strong>Contact</strong>: dcasanueva@us.es
</p>


<h2 name="Instalation">Instalation</h2>
<p align="justify">
<ol>
	<li>Have or have access to the SpiNNaker hardware platform. In case of local use, follow the installation instructions available on the <a href="http://spinnakermanchester.github.io/spynnaker/6.0.0/index.html">official website</a></li>
	<li>Python version 3.8.10</li>
	<li>Python libraries:</li>
	<ul>
		<li><strong>sPyNNaker</strong></li>
		<li><strong>numpy</strong> 1.21.4</li>
		<li><strong>matplotlib</strong> 3.5.0</li>
		<li><strong>xlsxWriter</strong> 3.0.2</li>
	</ul>
</ol>
</p>
<p align="justify">
To run any script, follow the python nomenclature: <code>python script.py</code>
</p>


<h2 name="RepositoryContent">Repository content</h3>
<p align="justify">
<ul>
	<li><p align="justify"><a href="CA3_content_addressable.py">CA3_content_addressable.py</a>: class that is responsible for the construction of the content-addressable memory module.</p></li>
	<li><p align="justify"><a href="test_CA3_content_addressable.py">test_CA3_content_addressable.py</a>: script in charge of carrying out the simulation of the memory model and the plotting of the necessary graphics of the simulation. The configuration of the model can be found on <a href="config/network_config.json">network_config.json</a> and the visual representation of the test can be found on <a href="results/">result</a> folder.</p></li>
	<li><p align="justify"><a href="generate_testbench.py">generate_testbench.py</a>: script in charge of generating the file with the input spikes of the memory model (in <a href="tb/">tb</a> folder) needed to perform the testbench.</p></li>
	<li><p align="justify"><a href="plot.py">plot.py</a>: functions needed to generate the plots used to understand the correct functioning of the memory model and in the article. For each experiment, the configuration of the spikes_plot function has to be change. The functions with the custom parameters for each experiment can be found on the <a href="spikes_plot.txt">spikes_plot</a> file.</p></li>
	<li><p align="justify"><a href="excel_controller.py">excel_controller.py</a>: set of functions used as a tool for the generation of excel files summarising the result of the experimentation.</p></li>
</ul>
</p>


<h2 name="Usage">Usage</h2>
<p align="justify">
To perform memory tests, run <a href="test_CA3_content_addressable.py">test_CA3_content_addressable.py</a>. This script is in charge of building the memory model, i.e. calling <a href="CA3_content_addressable.py">CA3_content_addressable.py</a>, run the simulation and create the necessary visual resources on the simulation result. 
</p>
<p align="justify">
The <strong>experiment</strong> parameter indicates the experiment to be simulated, change this parameter to switch from one to the other. The available experiments are commented inside the script. The <strong>recordWeight</strong> parameter for each experiment indicate if record the weight of the STDP synapses in order to get the evolution of that synapses along the experiment in a plot.
</p>
<p align="justify">
Finally, in order to be able to use the memory model as a module within a larger SNN network, we have developed a python package that includes this memory model (among others): sPyMem. You can install sPyMem via pip thanks to its <a href="https://pypi.org/project/sPyMem/">PyPi</a> distribution: <code>pip install sPyMem</code> or download it from source on their <a href="https://github.com/dancasmor/sPyMem/">github repository</a>. In this package, the memory model presented in this paper would be called <strong>CA3_content_addressable</strong>.
</p>


<h2 name="CiteThisWork">Cite this work</h2>
<p align="justify">
Work in progress...
</p>


<h2 name="Credits">Credits</h2>
<p align="justify">
The author of the original idea is Daniel Casanueva-Morato while working on a research project of the <a href="http://www.rtc.us.es/">RTC Group</a>.

This research was partially supported by the Spanish grant MINDROB (PID2019-105556GB-C33/AEI/10.13039/501100011033). 

D. C.-M. was supported by a "Formación de Profesor Universitario" Scholarship from the Spanish Ministry of Education, Culture and Sport.
</p>


<h2 name="License">License</h2>
<p align="justify">
This project is licensed under the GPL License - see the <a href="https://github.com/dancasmor/An-aproach-to-a-spike-based-Content-Addressable-Memory-bio-inspired-in-the-Hippocampus/blob/main/LICENSE">LICENSE.md</a> file for details.
</p>
<p align="justify">
Copyright © 2023 Daniel Casanueva-Morato<br>  
<a href="mailto:dcasanueva@us.es">dcasanueva@us.es</a>
</p>

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
