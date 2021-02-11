# grafana-env
Keep consistent copies of Grafana dashboards between production and development environments.

To run, create JSON files of your production and development Grafana JSON models. Then,
run the following command. Note: result will be output to `stdout`:
```
python3 grafana_env.py --prod_json <prod_json_path> --dev_json <dev_json_path> > result.json
```
