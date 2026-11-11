"""The Economist-stil for matplotlib. Importer modulen for aa aktivere stilen.

Dette er malen din med to smaa tillegg:
  * 'Liberation Sans' i font.sans-serif (Arial-kompatibel, finnes paa GitHub-runneren)
  * source_y i economist_title, med samme standardverdi som foer (-0.12), slik at kilden
    kan flyttes ned naar en figur har x-akseetikett
"""
import matplotlib as mpl

# -- The Economist style ------------------------------------------------------
ECONOMIST_RED = "#E3120B"
ECONOMIST_BLUE = "#006BA2"
ECONOMIST_GREY = "#D4D4D4"
ECONOMIST_DARK = "#121212"
ECONOMIST_BG = "#F2F2EF"

mpl.rcParams.update({
    'figure.facecolor':      ECONOMIST_BG,
    'figure.figsize':        (12, 6),
    'figure.dpi':            150,
    'axes.facecolor':        ECONOMIST_BG,
    'axes.edgecolor':        ECONOMIST_DARK,
    'axes.linewidth':        0.8,
    'axes.spines.top':       False,
    'axes.spines.right':     False,
    'axes.spines.left':      False,
    'axes.grid':             True,
    'axes.grid.axis':        'y',
    'axes.labelcolor':       ECONOMIST_DARK,
    'axes.labelsize':        11,
    'axes.titlesize':        13,
    'axes.titleweight':      'bold',
    'axes.titlepad':         12,
    'axes.prop_cycle':       mpl.cycler(color=[
                                 ECONOMIST_BLUE,
                                 ECONOMIST_RED,
                                 '#3EBCD2',
                                 '#379A8B',
                                 '#EBB434',
                                 '#9A607F',
                                 '#758D99',
                             ]),
    'grid.color':            ECONOMIST_GREY,
    'grid.linewidth':        0.8,
    'grid.alpha':            0.7,
    'xtick.color':           ECONOMIST_DARK,
    'ytick.color':           ECONOMIST_DARK,
    'xtick.labelsize':       10,
    'ytick.labelsize':       10,
    'xtick.bottom':          True,
    'ytick.left':            False,
    'xtick.major.size':      4,
    'xtick.major.width':     0.8,
    'legend.frameon':        False,
    'legend.fontsize':       10,
    'legend.labelcolor':     ECONOMIST_DARK,
    'lines.linewidth':       1.8,
    'lines.solid_capstyle':  'round',
    'font.family':           'sans-serif',
    'font.sans-serif':       ['Arial', 'Helvetica Neue', 'Helvetica', 'Liberation Sans', 'DejaVu Sans'],
    'text.color':            ECONOMIST_DARK,
})


def economist_title(ax, title, subtitle=None, source=None, source_y=-0.12):
    """Economist-style title: red top bar, bold title, optional subtitle and source."""
    ax.set_title(title, loc='left', fontweight='bold',
                 fontsize=13, color=ECONOMIST_DARK, pad=16)
    if subtitle:
        ax.annotate(subtitle, xy=(0, 1), xycoords='axes fraction',
                    fontsize=10, color='#4D4D4D', style='italic',
                    annotation_clip=False)
    ax.annotate('', xy=(0, 1.13), xycoords='axes fraction',
                xytext=(1, 1.13), textcoords='axes fraction',
                arrowprops=dict(arrowstyle='-', color=ECONOMIST_RED, lw=3),
                annotation_clip=False)
    if source:
        ax.annotate(f'Source: {source}',
                    xy=(0, source_y), xycoords='axes fraction',
                    fontsize=8, color='#4D4D4D',
                    annotation_clip=False)
