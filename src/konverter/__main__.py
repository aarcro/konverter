import click

from .app import Konverter


def recursive_merge(d1, d2):
    merged = d1.copy()
    for key, value in d2.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = recursive_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def parse_dotted_key_value(ctx, param, value):
    # `-e foo.bar=true` -->  `{"foo": {"bar": True}}`
    result = {}
    if not value:
        return result

    for item in value:
        key, val = item.split("=")
        keys = key.strip().split(".")
        current = result
        for k in keys[:-1]:
            current = current.setdefault(k, {})

        # If true or false, convert to boolean
        val = val.strip()
        if val.lower() == "true":
            val = True
        elif val.lower() == "false":
            val = False

        current[keys[-1]] = val
    return result

@click.command()
@click.argument("config_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-c",
    "--context",
    multiple=True,
    help="dotted.key=value to override in the template context",
    callback=parse_dotted_key_value,
)
def cli(config_path: str, context: list[tuple[str, str]]) -> None:
    app = Konverter.from_file(config_path)
    # Any cli -e options override context on disk
    app.context = recursive_merge(app.context, context)
    app.render(click.get_text_stream("stdout"))


if __name__ == "__main__":
    cli()
