# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Emulab specific extensions.
import geni.rspec.emulab as emulab
# Route specific extensions.
import geni.rspec.emulab.route as route

OSIMAGE = 'urn:publicid:IDN+emulab.net+image+PowderTeam:cots-focal-image'

#
# Install script from the repository. This installs the uhd tools,
# gnuradio, and starts up uhd_fft (displayed in the X11 VNC console).
#
INSTALL = 'sudo /bin/bash /local/repository/install.sh'

# Create a Request object to start building the RSpec.
request = portal.context.makeRequestRSpec()

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
