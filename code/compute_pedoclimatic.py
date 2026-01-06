import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import rasterstats

import GLOBALS


def compute_pedoclimatic_mix_france(
    bioregion_path: Path = GLOBALS.BIOREGION_FRANCE_PATH,
    wrb_raster_path: Path = GLOBALS.WRB_LV1_FRANCE_PATH,
    wrb_mapping_path: Path = GLOBALS.WRB_FINAL_MAPPING_PATH,
) -> pd.DataFrame:
    """
    Compute the national soil-class composition across French climate zones.

    Returns a DataFrame indexed by (climate, soil_class) with:
      - pixel_count
      - relative_pixel_count (national share; sums to 1 across all rows)
      - cumulative_area_pct (cumulative national share after sorting desc)
    """
    # get climate zones (index = climate code)
    bioregions_france = gpd.read_file(bioregion_path).set_index("code")["geometry"]

    # soil-class mapping for raster categories
    with open(wrb_mapping_path, "r", encoding="utf-8") as file:
        mapping_raw = json.load(file)
    mapping = {int(k): v for k, v in mapping_raw.items()}

    # compute zonal statistics to get the pixel count for each climate zone and each soil class
    stats = rasterstats.zonal_stats(
        vectors=bioregions_france,
        raster=wrb_raster_path,
        categorical=True,
        category_map=mapping,
        geojson_out=True,
    )

    # transform the stats output (complex format) into a dataframe
    rows: list[tuple[str, str, int]] = []
    for climate in stats:
        climate: str = climate["id"]
        props: dict = climate["properties"]

        # Keep only histogram entries (counts). This avoids pulling non-count attributes into the table.
        for soil_class, pixelcount in props.items():
            if isinstance(pixelcount, (int, float)):
                rows.append((climate, soil_class, int(pixelcount)))

    pedoclimatic_data = (
        pd.DataFrame(rows, columns=["climate", "soil_class", "pixel_count"])
        .set_index(["climate", "soil_class"])
    )

    # compute relative values, relative pixel count is used to proxy relative surface coverage
    pedoclimatic_data["relative_pixel_count"] = pedoclimatic_data["pixel_count"].transform(lambda x: x/x.sum())
    pedoclimatic_data.sort_values(by="relative_pixel_count", ascending=False, inplace=True)
    pedoclimatic_data["cumulative_area_pct"] = pedoclimatic_data["relative_pixel_count"].cumsum()

    return pedoclimatic_data


if __name__ == "__main__":
    pedoclimatic_mix_df = compute_pedoclimatic_mix_france()

    # Write to disk
    outfile: Path = GLOBALS.PEDOCLIM_STATS_PATH
    print(f"Writing {outfile}")
    pedoclimatic_mix_df.to_csv(outfile, float_format="{:.3f}".format)
