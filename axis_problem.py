
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

#########################################
## Definitions
#########################################
color_pattern = ['#FFFF00', '#FF00FF', '#55FF55', '#00FFFF', '#5555FF',
                '#5500FF', '#FF5555', '#0000FF', '#FFAA00', '#000000']

axis_locations = ['left', 'right', 'left', 'right',]

plot = None
views = []
axes = []
curves = []
single_axis = True
axis_mode = 'single'

plots = 0
data = np.random.normal(size=(10,1000))

#########################################
## Functions
#########################################
def setup_plot_single_axis(plot, names):
    """
    Setup items for single Y axis plot.

    :names: (list -> strings) List of channels to be displayed.
    :return: (None)
    """
    global curves
    for i in range(len(names)):
        if names[i] != "None":
            curve = plot.plot(pen=color_pattern[i])
            curve.plotdata_ave = None
            curves.append(curve)

    return plot, curves

def setup_plot_multi_axis(gl, names):
    """
    Setup items for multiple Y axis plot.

    :names: (list -> strings) List of channels to bi displayed. "None" should be used to ignore that channel.
    :return: (None)
    """
    global views, axes, curves, plot

    # We do not use default axis
    plot.hideAxis('left')

    # Create axis and views
    left_axis = []
    right_axis = []
    for i, field_name in enumerate(names):
        # Skip if None was selected
        if field_name == "None":
            continue
        axis = pg.AxisItem(axis_locations[i])
        axis.setLabel(f"Channel {i+1} [{field_name}]", color=color_pattern[i])
        if axis_locations[i] == "left":
            left_axis.append(axis)
        else:
            right_axis.append(axis)
        axes.append(axis)
        # First view we take from plotItem
        if len(axes) == 1:
            views.append(plot.vb)
        else:
            views.append(pg.ViewBox())

    # Add axis and plot to GraphicsLayout (self.ci)
    # Order how they are added is important, while it is also important
    # we hold correct order (the same as in the "names" variable) in self.axis
    # variable as other code depends on this.
    for a in left_axis:
        gl.addItem(a)
    gl.addItem(plot)
    for a in right_axis:
        gl.addItem(a)

    # Add Viewboxes to the layout
    for vb in views:
        if vb != plot.vb:
            gl.scene().addItem(vb)

    # Link axis to view boxes
    for i, view in enumerate(views):
        axes[i].linkToView(view)
        if view != plot.vb:
            view.setXLink(plot.vb)

    # Make curves
    count = 0
    for i, field_name in enumerate(names):
        if field_name == "None":
            continue
        curve = pg.PlotCurveItem(pen=color_pattern[i])
        curve.plotdata_ave = None
        left_curve = []
        right_curve = []
        if axis_locations[i] == "left":
            left_curve.append(curve)
        else:
            right_curve.append(curve)
        curves.extend(left_curve)
        curves.extend(right_curve)
        views[count].addItem(curve)
        count += 1

def update_views(plot):
    """
    Update the view so they scale properly.

    :return:
    """
    global views
    for view in views:
        if view == plot.vb:
            continue
        view.setGeometry(plot.vb.sceneBoundingRect())

def build_plot(gl, names, single):

    global plot, views, axis, curves, single_axis

    # Delete existing plots
    if single_axis:
        for curve in curves:
            plot.removeItem(curve)
    else:
        # Delete old plots if exists
        for i, view in enumerate(views):
            view.removeItem(curves[i])

        for a in axes:
            try:
                gl.removeItem(a)
            except:
                pass
    # Remove plotItem
    if plot is not None:
        gl.removeItem(plot)

    # Remove references to all chart items
    views = []
    axis = []
    curves = []

    # Create plot item
    plot = pg.PlotItem()
    plot.showGrid(x=True, y=True)

    # Generate plot items
    single_axis = single
    if single:
        setup_plot_single_axis(plot, names)
    else:
        setup_plot_multi_axis(win, names)

    # Update plots
    plot.vb.sigResized.connect(update_views)
    update_views(plot)


#########################################
## Example
#########################################
# App
app = QtGui.QApplication([])

# Window
win = pg.GraphicsLayoutWidget(show=True, title="Axis problem v0.11.0")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')


# Build plot
build_plot(win, ["c1", "c2", "c3", "c4",], True)
win.addItem(plot)

# Update data
def update():
    global win, plot, curves, plots, data, single_axis
    for i, curve in enumerate(curves):
        curve.setData(data[plots%10]*i)
    if plots == 0:
        plot.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    plots += 1

    if plots % 20 == 0:
        build_plot(win, ["c1", "c2", "c3", "c4",], not single_axis)
        win.addItem(plot)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(500)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
