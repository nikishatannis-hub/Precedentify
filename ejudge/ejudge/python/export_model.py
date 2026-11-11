"""
OPTIONAL: build the augmented ONNX file (model + tokenizer) that Oracle needs.

Requires the OML4Py *client* (Linux/Python 3.12 per Oracle docs) - see
https://docs.oracle.com/en/database/oracle/machine-learning/oml4py/
Alternatively download Oracle's pre-built augmented MiniLM ONNX zip from the
Oracle AI Vector Search documentation and skip this script.

Usage:  python export_model.py models/
"""
import sys

from oml.utils import ONNXPipeline, ONNXPipelineConfig  # from OML4Py client

out_dir = sys.argv[1] if len(sys.argv) > 1 else "models"

pipeline = ONNXPipeline(model_name="sentence-transformers/all-MiniLM-L6-v2")
pipeline.export2file("all_MiniLM_L6_v2", output_dir=out_dir)
print(f"Wrote {out_dir}/all_MiniLM_L6_v2.onnx")
