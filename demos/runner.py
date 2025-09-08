class DemoResult:
    def __init__(self, metrics):
        self.metrics = metrics

class DemoRunner:
    def __init__(self, scenario_config, app_config):
        self.scenario_config = scenario_config
        self.app_config = app_config

    async def execute(self, output_dir, interactive):
        print(f"Executing demo with scenario {self.scenario_config} and app_config {self.app_config}")
        print(f"Output directory: {output_dir}")
        print(f"Interactive: {interactive}")
        return DemoResult(metrics={"duration": 10, "files_generated": 2})
