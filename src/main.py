import click
import logging
from getigc.get_syride_igc import Syride
from filterigc.filter_igc import FilterIgc

logger = logging.getLogger("get-igc")
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

@click.group()
def cli():
    pass

@cli.command()
@click.option("--min-distance", required=True, type=int)
@click.option("--max-distance", required=False, type=int, default=1000)
@click.option("--min-plafond", required=True, type=int)
@click.option("--spot-id", required=True, type=str)
@click.option("--max-trace-to-get", required=False, type=int, default=10)
@click.option("--output-dir", required=True, type=str)
def get_syride_igc(min_distance, max_distance, min_plafond, spot_id, max_trace_to_get, output_dir):
    logger.debug(
        f"Parameters :  min_plaf : {min_plafond}, min_distance: {min_distance}, max_distance: {max_distance}, spot_id : {spot_id}, max_trace_to_get: {max_trace_to_get}"
    )
    syride = Syride(min_distance, max_distance, min_plafond, spot_id, max_trace_to_get, output_dir)
    syride.getFlights()

@cli.command()
@click.option("--input-dir", required=True, type=str)
@click.option("--distance-min-between-takeoff-and-landing", required=False, type=int)
def filterigc(input_dir, distance_min_between_takeoff_and_landing):
    logger.debug("On commence")
    filterIgc = FilterIgc(input_dir)
    filterIgc.filter()

if __name__ == "__main__":
    cli()
