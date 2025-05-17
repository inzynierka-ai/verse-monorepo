import logging
from typing import Dict, Any
from .workflow_loader import WorkflowLoader


class LocationWorkflowLoader(WorkflowLoader):
    """Loader for location generation workflows"""
    
    def __init__(self):
        super().__init__()
        self.workflow_file = "locations_api.json"
    
    def load_workflow(self, prompt: str, generation_id: str) -> Dict[str, Any]:
        """Load a location workflow and customize it with the given prompt"""
        workflow = self._load_workflow_file(self.workflow_file)
        
        if not workflow:
            logging.warning(f"Location workflow not found, using fallback")
            return {}
        
        # Customize the workflow with the prompt and random parameters
        random_seed = self._generate_random_seed()
        
        # Find the text encode node (typically contains the prompt)
        for _, node in workflow.items():
            if node.get("class_type") == "CLIPTextEncode" and "text" in node.get("inputs", {}):
                # Don't override an empty negative prompt
                if node["inputs"]["text"] != "":
                    node["inputs"]["text"] = prompt
        
        # Find the KSampler node to update random parameters
        for _, node in workflow.items():
            if node.get("class_type") == "KSampler":
                node["inputs"]["seed"] = random_seed
                node["inputs"]["steps"] = self._get_random_steps()
                node["inputs"]["cfg"] = self._get_random_cfg()
                node["inputs"]["sampler_name"] = self._get_random_sampler()
        
        # Find the SaveImage node (if any) to add our generation ID
        for _, node in workflow.items():
            if node.get("class_type") == "SaveImage":
                node["inputs"]["filename_prefix"] = f"location_{generation_id}_{random_seed}"
                break
        else:
            # If no SaveImage node, add one connecting to the output node
            output_node_id = self._find_output_node_id(workflow)
            if output_node_id:
                new_node_id = str(max(int(k) for k in workflow.keys()) + 1)
                workflow[new_node_id] = {
                    "class_type": "SaveImage",
                    "inputs": {
                        "filename_prefix": f"location_{generation_id}_{random_seed}",
                        "images": [output_node_id, 0]
                    }
                }
        
        return workflow 