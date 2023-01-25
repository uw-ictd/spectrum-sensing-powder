# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Emulab specific extensions.
import geni.rspec.emulab as emulab
# Route specific extensions.
import geni.rspec.emulab.route as route

import os

# Create the PC object
pc = portal.Context()


OSIMAGE = 'urn:publicid:IDN+emulab.net+image+PowderTeam:cots-focal-image'

#
# Install script from the repository. This installs the uhd tools,
# gnuradio, and starts up uhd_fft (displayed in the X11 VNC console).
#
INSTALL = 'sudo /bin/bash /local/repository/install.sh'


BIN_PATH = "/local/repository/bin"
ETC_PATH = "/local/repository/etc"
LOWLAT_IMG = "urn:publicid:IDN+emulab.net+image+PowderTeam:U18LL-SRSLTE"
UBUNTU_IMG = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD"
COTS_UE_IMG = "urn:publicid:IDN+emulab.net+image+PowderTeam:cots-base-image"
COMP_MANAGER_ID = "urn:publicid:IDN+emulab.net+authority+cm"
# hash includes fix for avx build patch issue
#TODO: check if merged to develop
DEFAULT_NR_RAN_HASH = "565b8482f926bea13b5b72e4a6651032fdac7083"
DEFAULT_NR_CN_HASH = "v1.4.0"
OAI_DEPLOY_SCRIPT = os.path.join(BIN_PATH, "deploy-oai.sh")
OPEN5GS_DEPLOY_SCRIPT = os.path.join(BIN_PATH, "deploy-open5gs.sh")

NUM_CNS = None

def gnb_cn_pair(idx, b210_node):
    # role = "cn"
    cn_node = request.RawPC("cn5g-{}".format(b210_node.device.split("-")[-1]))
    cn_node.component_manager_id = COMP_MANAGER_ID
    cn_node.hardware_type = params.cn_nodetype
    cn_node.disk_image = UBUNTU_IMG
    cn_if = cn_node.addInterface("cn-if-{}".format(idx))
    idx  = idx + 1
    cn_if.addAddress(rspec.IPv4Address("192.168.1.{}".format(idx), "255.255.255.0"))
    cn_link = request.Link("cn-link-{}".format(idx))
    cn_link.bandwidth = 1*1000*1000
    cn_link.addInterface(cn_if)

    if params.oai_cn_commit_hash:
        oai_cn_hash = params.oai_cn_commit_hash
    else:
        oai_cn_hash = DEFAULT_NR_CN_HASH

    # cmd = "{} '{}' {}".format(OAI_DEPLOY_SCRIPT, oai_cn_hash, role)
    cn_node.addService(rspec.Execute(shell="bash", command=OPEN5GS_DEPLOY_SCRIPT))

    node = request.RawPC("gnb-{}".format(b210_node.device.split("-")[-1]))
    node.component_manager_id = COMP_MANAGER_ID
    node.component_id = b210_node.device

    if params.sdr_compute_image:
        node.disk_image = params.sdr_compute_image
    else:
        node.disk_image = LOWLAT_IMG

    nodeb_cn_if = node.addInterface("nodeb-cn-if")
    gnb_idx = idx + 1 + NUM_CNS
    nodeb_cn_if.addAddress(rspec.IPv4Address("192.168.1.{}".format(gnb_idx), "255.255.255.0"))
    cn_link.addInterface(nodeb_cn_if)

    if params.oai_ran_commit_hash:
        oai_ran_hash = params.oai_ran_commit_hash
    else:
        oai_ran_hash = DEFAULT_NR_RAN_HASH

    cmd = "{} '{}' {}".format(OAI_DEPLOY_SCRIPT, oai_ran_hash, "nodeb")
    node.addService(rspec.Execute(shell="bash", command=cmd))
    node.addService(rspec.Execute(shell="bash", command="/local/repository/bin/tune-cpu.sh"))





node_types = [
    ("d430", "Emulab, d430"),
    ("d740", "Emulab, d740"),
]

pc.defineParameter(
    name="cn_nodetype",
    description="Type of compute node to use for CN node (if included)",
    typ=portal.ParameterType.STRING,
    defaultValue=node_types[0],
    legalValues=node_types
)

pc.defineParameter(
    name="oai_ran_commit_hash",
    description="Commit hash for OAI RAN",
    typ=portal.ParameterType.STRING,
    defaultValue="",
    advanced=True
)

pc.defineParameter(
    name="oai_cn_commit_hash",
    description="Commit hash for OAI (5G)CN",
    typ=portal.ParameterType.STRING,
    defaultValue="",
    advanced=True
)

pc.defineParameter(
    name="sdr_compute_image",
    description="Image to use for compute connected to SDRs",
    typ=portal.ParameterType.STRING,
    defaultValue="",
    advanced=True
)

dense_radios = [
    ("cnode-wasatch",
     "Wasatch"),
    ("cnode-mario",
     "Mario"),
    ("cnode-moran",
     "Moran"),
    ("cnode-guesthouse",
     "Guesthouse"),
    ("cnode-ebc",
     "EBC"),
    ("cnode-ustar",
     "USTAR"),
]

pc.defineStructParameter(
    "dense_radios", "Dense Site Radios", [],
    multiValue=True,
    min=1,
    multiValueTitle="Dense Site NUC+B210 radios to allocate.",
    members=[
        portal.Parameter(
            "device",
            "SFF Compute + NI B210 device",
            portal.ParameterType.STRING,
            dense_radios[0], dense_radios,
            longDescription="A Small Form Factor compute with attached NI B210 device at the given Dense Deployment site will be allocated."
        ),
    ]
)

portal.context.defineStructParameter(
    "freq_ranges", "Frequency Ranges To Transmit In",
    defaultValue=[{"freq_min": 3430.0, "freq_max": 3470.0}],
    multiValue=True,
    min=0,
    multiValueTitle="Frequency ranges to be used for transmission.",
    members=[
        portal.Parameter(
            "freq_min",
            "Frequency Range Min",
            portal.ParameterType.BANDWIDTH,
            3430.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Frequency Range Max",
            portal.ParameterType.BANDWIDTH,
            3470.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ]
)

params = pc.bindParameters()
pc.verifyParameters()

request = pc.makeRequestRSpec()


NUM_CNS = len(params.dense_radios)

for idx, dense_radio in enumerate(params.dense_radios):
        gnb_cn_pair(idx, dense_radio)

for frange in params.freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

tour = IG.Tour()
tour.Description(IG.Tour.MARKDOWN, tourDescription)
tour.Instructions(IG.Tour.MARKDOWN, tourInstructions)

request.addTour(tour)
#
# Declare that you will be starting X11 VNC on (some of) your nodes.
# You must have this line for X11 VNC to work.
#
request.initVNC()

#
# Request all bus routes. On a typical day, 4-6 buses are running across
# a few common routes. Morning is when the most buses run.
#
allroutes = request.requestAllRoutes()
allroutes.disk_image = OSIMAGE
allroutes.addService(pg.Execute(shell="sh", command=INSTALL))
allroutes.startVNC()

portal.context.printRequestRSpec()
