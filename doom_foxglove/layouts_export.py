"""Write stock Foxglove Play, Debug, and Replay layouts under layouts/."""

from __future__ import annotations

import json
from pathlib import Path

import foxglove.layouts as fl

from doom_foxglove import CAMERA_TOPIC, CMD_VEL_TOPIC, ENTITIES_TOPIC, LOG_TOPIC, MAP_TOPIC, PLAYER_TOPIC, WALLS_TOPIC


def _image() -> fl.ImagePanel:
    return fl.ImagePanel(
        title="Camera",
        config=fl.ImageConfig(
            image_mode=fl.ImageModeConfig(image_topic=CAMERA_TOPIC),
        ),
    )


def _teleop() -> fl.TeleopPanel:
    return fl.TeleopPanel(
        title="Teleop",
        config=fl.TeleopConfig(
            topic=CMD_VEL_TOPIC,
            publish_rate=35,
            up_button=fl.TeleopButton(field="linear-x", value=1.0),
            down_button=fl.TeleopButton(field="linear-x", value=-1.0),
            left_button=fl.TeleopButton(field="angular-z", value=1.0),
            right_button=fl.TeleopButton(field="angular-z", value=-1.0),
            stop_button=fl.TeleopButton(field="linear-x", value=0.0),
            auto_send_stop_on_release=True,
        ),
    )


def _gauge(title: str, field: str, maximum: float) -> fl.GaugePanel:
    return fl.GaugePanel(
        title=title,
        config=fl.GaugeConfig(
            path=f"{PLAYER_TOPIC}.{field}",
            style="dial",
            min_value=0,
            max_value=maximum,
            color_mode="colormap",
            color_map="red-yellow-green",
        ),
    )


def _gauges() -> fl.SplitContainer:
    return fl.SplitContainer(
        direction="column",
        items=[
            fl.SplitItem(proportion=1, content=_gauge("Health", "health", 200)),
            fl.SplitItem(proportion=1, content=_gauge("Armor", "armor", 200)),
            fl.SplitItem(proportion=1, content=_gauge("Ammo", "ammo", 300)),
        ],
    )


def play_layout() -> fl.Layout:
    return fl.Layout(
        content=fl.SplitContainer(
            direction="row",
            items=[
                fl.SplitItem(proportion=3, content=_image()),
                fl.SplitItem(
                    proportion=1,
                    content=fl.SplitContainer(
                        direction="column",
                        items=[
                            fl.SplitItem(proportion=1, content=_teleop()),
                            fl.SplitItem(proportion=2, content=_gauges()),
                        ],
                    ),
                ),
            ],
        )
    )


def debug_layout() -> fl.Layout:
    scene = fl.ThreeDeePanel(
        title="Map",
        config=fl.ThreeDeeConfig(
            follow_tf="base_link",
            fixed_frame="map",
            follow_mode="follow-pose",
            topics={
                MAP_TOPIC: fl.BaseRendererGridTopicSettings(
                    visible=True,
                    color_mode="colormap",
                    color_field="occupancy",
                    color_map="turbo",
                    min_value=0,
                    max_value=100,
                    frame_locked=True,
                ),
                ENTITIES_TOPIC: fl.BaseRendererSceneUpdateTopicSettings(visible=True),
                WALLS_TOPIC: fl.BaseRendererSceneUpdateTopicSettings(visible=True),
            },
        ),
    )
    plot = fl.PlotPanel(
        title="Health",
        config=fl.PlotConfig(
            paths=[
                fl.PlotSeries(value=f"{PLAYER_TOPIC}.health", label="health"),
                fl.PlotSeries(value=f"{PLAYER_TOPIC}.ammo", label="ammo"),
            ],
            x_axis_val="timestamp",
            show_legend=True,
        ),
    )
    log = fl.LogPanel(
        title="Log",
        config=fl.LogConfig(topic_to_render=LOG_TOPIC, min_log_level=1),
    )
    raw = fl.RawMessagesPanel(
        title="Player",
        config=fl.RawMessagesConfig(topic_path=PLAYER_TOPIC, expansion="all"),
    )
    return fl.Layout(
        content=fl.SplitContainer(
            direction="column",
            items=[
                fl.SplitItem(
                    proportion=3,
                    content=fl.SplitContainer(
                        direction="row",
                        items=[
                            fl.SplitItem(proportion=2, content=_image()),
                            fl.SplitItem(proportion=2, content=scene),
                            fl.SplitItem(
                                proportion=1,
                                content=fl.SplitContainer(
                                    direction="column",
                                    items=[
                                        fl.SplitItem(proportion=1, content=_teleop()),
                                        fl.SplitItem(proportion=2, content=_gauges()),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
                fl.SplitItem(
                    proportion=1,
                    content=fl.SplitContainer(
                        direction="row",
                        items=[
                            fl.SplitItem(proportion=1, content=plot),
                            fl.SplitItem(proportion=1, content=log),
                            fl.SplitItem(proportion=1, content=raw),
                        ],
                    ),
                ),
            ],
        )
    )


def replay_layout() -> fl.Layout:
    """File playback: camera, 3D, gauges, log. Teleop is hidden. Playback bar is Foxglove's."""
    scene = fl.ThreeDeePanel(
        title="Map",
        config=fl.ThreeDeeConfig(
            follow_tf="base_link",
            fixed_frame="map",
            follow_mode="follow-pose",
            topics={
                MAP_TOPIC: fl.BaseRendererGridTopicSettings(
                    visible=True,
                    color_mode="colormap",
                    color_field="occupancy",
                    color_map="turbo",
                    min_value=0,
                    max_value=100,
                    frame_locked=True,
                ),
                ENTITIES_TOPIC: fl.BaseRendererSceneUpdateTopicSettings(visible=True),
                WALLS_TOPIC: fl.BaseRendererSceneUpdateTopicSettings(visible=True),
            },
        ),
    )
    plot = fl.PlotPanel(
        title="Health",
        config=fl.PlotConfig(
            paths=[
                fl.PlotSeries(value=f"{PLAYER_TOPIC}.health", label="health"),
                fl.PlotSeries(value=f"{PLAYER_TOPIC}.ammo", label="ammo"),
            ],
            x_axis_val="timestamp",
            show_legend=True,
        ),
    )
    log = fl.LogPanel(
        title="Log",
        config=fl.LogConfig(topic_to_render=LOG_TOPIC, min_log_level=1),
    )
    raw = fl.RawMessagesPanel(
        title="Player",
        config=fl.RawMessagesConfig(topic_path=PLAYER_TOPIC, expansion="all"),
    )
    return fl.Layout(
        content=fl.SplitContainer(
            direction="column",
            items=[
                fl.SplitItem(
                    proportion=3,
                    content=fl.SplitContainer(
                        direction="row",
                        items=[
                            fl.SplitItem(proportion=2, content=_image()),
                            fl.SplitItem(proportion=2, content=scene),
                            fl.SplitItem(proportion=1, content=_gauges()),
                        ],
                    ),
                ),
                fl.SplitItem(
                    proportion=1,
                    content=fl.SplitContainer(
                        direction="row",
                        items=[
                            fl.SplitItem(proportion=1, content=plot),
                            fl.SplitItem(proportion=1, content=log),
                            fl.SplitItem(proportion=1, content=raw),
                        ],
                    ),
                ),
            ],
        )
    )


def write_layouts(root: Path | None = None) -> list[Path]:
    dest = root or Path(__file__).resolve().parents[1] / "layouts"
    dest.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, layout in (
        ("Play.json", play_layout()),
        ("Debug.json", debug_layout()),
        ("Replay.json", replay_layout()),
    ):
        path = dest / name
        payload = json.loads(layout.to_json())
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    for path in write_layouts():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
