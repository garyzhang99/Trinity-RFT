import streamlit as st

from trinity.common.constants import SyncMethod
from trinity.manager.config_registry.config_registry import CONFIG_GENERATORS
from trinity.manager.config_registry.model_config_manager import set_trainer_gpu_num


def explorer_visible() -> bool:
    return st.session_state["mode"] == "both"


@CONFIG_GENERATORS.register_config(default_value=8, visible=explorer_visible)
def set_runner_per_model(**kwargs):
    st.number_input("Runner per Model", min_value=1, **kwargs)


@CONFIG_GENERATORS.register_config(default_value=900, visible=explorer_visible)
def set_max_timeout(**kwargs):
    st.number_input("Max Timeout", min_value=0, **kwargs)


@CONFIG_GENERATORS.register_config(default_value=2, visible=explorer_visible)
def set_explorer_max_retry_times(**kwargs):
    st.number_input("Explorer Max Retry Times", min_value=0, **kwargs)


@CONFIG_GENERATORS.register_config(default_value=1000, visible=explorer_visible)
def set_eval_interval(**kwargs):
    st.number_input("Eval Interval", min_value=1, **kwargs)


@CONFIG_GENERATORS.register_config(default_value=True, visible=explorer_visible)
def set_bench_on_latest_checkpoint(**kwargs):
    st.checkbox("Eval on Latest Checkpoint", **kwargs)


@CONFIG_GENERATORS.register_config(default_value="vllm_async", visible=explorer_visible)
def set_engine_type(**kwargs):
    st.selectbox("Engine Type", ["vllm_async", "vllm"], **kwargs)


@CONFIG_GENERATORS.register_config(default_value=2, visible=explorer_visible)
def set_engine_num(**kwargs):
    key = kwargs.get("key")
    total_gpu_num = st.session_state["total_gpu_num"]
    max_engine_num = (total_gpu_num - 1) // st.session_state["tensor_parallel_size"]
    if st.session_state[key] > max_engine_num:
        st.session_state[key] = max_engine_num
        set_trainer_gpu_num()
    st.number_input(
        "Engine Num",
        min_value=1,
        max_value=max_engine_num,
        on_change=set_trainer_gpu_num,
        **kwargs,
    )


@CONFIG_GENERATORS.register_config(default_value=1, visible=explorer_visible)
def set_tensor_parallel_size(**kwargs):
    key = kwargs.get("key")
    total_gpu_num = st.session_state["total_gpu_num"]
    max_tensor_parallel_size = (total_gpu_num - 1) // st.session_state["engine_num"]
    if st.session_state[key] > max_tensor_parallel_size:
        st.session_state[key] = max_tensor_parallel_size
        set_trainer_gpu_num()
    st.number_input(
        "Tensor Parallel Size",
        min_value=1,
        max_value=max_tensor_parallel_size,
        on_change=set_trainer_gpu_num,
        **kwargs,
    )


@CONFIG_GENERATORS.register_check()
def check_tensor_parallel_size(unfinished_fields: set, key: str):
    if st.session_state["trainer_gpu_num"] <= 0:
        unfinished_fields.add("engine_num")
        unfinished_fields.add("tensor_parallel_size")
        st.warning(
            "Please check the settings of each `engine_num` and `tensor_marallel_size` to ensure that at least one GPU is reserved for the `trainer`."
        )
    elif (
        st.session_state["node_num"] > 1
        and st.session_state["trainer_gpu_num"] % st.session_state["gpu_per_node"] != 0
    ):
        unfinished_fields.add("engine_num")
        unfinished_fields.add("tensor_parallel_size")
        st.warning(
            "When `node_num > 1`, please check the settings of each `engine_num` and `tensor_marallel_size` to ensure that the number of GPUs reserved for the `trainer` is divisible by `gpu_per_node`"
        )


@CONFIG_GENERATORS.register_config(default_value=True, visible=explorer_visible)
def set_use_v1(**kwargs):
    st.checkbox("Use V1 Engine", **kwargs)


@CONFIG_GENERATORS.register_config(default_value=True, visible=explorer_visible)
def set_enforce_eager(**kwargs):
    st.checkbox("Enforce Eager", **kwargs)


@CONFIG_GENERATORS.register_config(default_value=False, visible=explorer_visible)
def set_enable_prefix_caching(**kwargs):
    st.checkbox("Prefix Caching", **kwargs)


@CONFIG_GENERATORS.register_config(default_value=False, visible=explorer_visible)
def set_enable_chunked_prefill(**kwargs):
    st.checkbox("Chunked Prefill", **kwargs)


@CONFIG_GENERATORS.register_config(default_value=0.9, visible=explorer_visible)
def set_gpu_memory_utilization(**kwargs):
    st.number_input("GPU Memory Utilization", min_value=0.0, max_value=1.0, **kwargs)


@CONFIG_GENERATORS.register_config(default_value="bfloat16", visible=explorer_visible)
def set_dtype(**kwargs):
    st.selectbox("Dtype", ["bfloat16", "float16", "float32"], **kwargs)


@CONFIG_GENERATORS.register_config(default_value=42, visible=explorer_visible)
def set_seed(**kwargs):
    st.number_input("Seed", step=1, **kwargs)


# TODO: max_prompt_tokens
# TODO: max_response_tokens
# TODO: chat_template


@CONFIG_GENERATORS.register_config(default_value=False, visible=explorer_visible)
def set_enable_thinking(**kwargs):
    st.checkbox("Enable Thinking For Qwen3", **kwargs)


@CONFIG_GENERATORS.register_config(default_value=False, visible=explorer_visible)
def set_enable_openai_api(**kwargs):
    st.checkbox("Enable OpenAI API", **kwargs)


def _set_auxiliary_model_idx(idx):
    col1, col2 = st.columns([9, 1])
    col1.text_input(
        "Model Path",
        key=f"auxiliary_model_{idx}_model_path",
    )
    if col2.button("✖️", key=f"auxiliary_model_{idx}_del_flag", type="primary"):
        st.rerun()

    engine_type_col, engine_num_col, tensor_parallel_size_col = st.columns(3)
    total_gpu_num = st.session_state["total_gpu_num"]
    engine_type_col.selectbox(
        "Engine Type", ["vllm_async"], key=f"auxiliary_model_{idx}_engine_type"
    )
    engine_num_col.number_input(
        "Engine Num",
        min_value=1,
        max_value=total_gpu_num - 1,
        on_change=set_trainer_gpu_num,
        key=f"auxiliary_model_{idx}_engine_num",
    )
    tensor_parallel_size_col.number_input(
        "Tensor Parallel Size",
        min_value=1,
        max_value=8,
        on_change=set_trainer_gpu_num,
        key=f"auxiliary_model_{idx}_tensor_parallel_size",
    )

    gpu_memory_utilization_col, dtype_col, seed_col = st.columns(3)
    gpu_memory_utilization_col.number_input(
        "GPU Memory Utilization",
        min_value=0.0,
        max_value=1.0,
        key=f"auxiliary_model_{idx}_gpu_memory_utilization",
    )
    dtype_col.selectbox(
        "Dtype", ["bfloat16", "float16", "float32"], key=f"auxiliary_model_{idx}_dtype"
    )
    seed_col.number_input("Seed", step=1, key=f"auxiliary_model_{idx}_seed")

    (
        use_v1_col,
        enforce_eager_col,
        enable_prefix_caching_col,
        enable_chunked_prefill_col,
    ) = st.columns(4)
    use_v1_col.checkbox("Use V1 Engine", key=f"auxiliary_model_{idx}_use_v1")
    enforce_eager_col.checkbox("Enforce Eager", key=f"auxiliary_model_{idx}_enforce_eager")
    enable_prefix_caching_col.checkbox(
        "Prefix Caching", key=f"auxiliary_model_{idx}_enable_prefix_caching"
    )
    enable_chunked_prefill_col.checkbox(
        "Chunked Prefill", key=f"auxiliary_model_{idx}_enable_chunked_prefill"
    )

    enable_thinking_col, enable_openai_api = st.columns(2)
    enable_thinking_col.checkbox(
        "Enable Thinking For Qwen3", key=f"auxiliary_model_{idx}_enable_thinking"
    )
    enable_openai_api.checkbox("Enable OpenAI API", key=f"auxiliary_model_{idx}_enable_openai_api")


@CONFIG_GENERATORS.register_config(other_configs={"_auxiliary_models_num": 0})
def set_auxiliary_models(**kwargs):
    if st.button("Add Auxiliary Models"):
        idx = st.session_state["_auxiliary_models_num"]
        st.session_state[f"auxiliary_model_{idx}_engine_num"] = 1
        st.session_state[f"auxiliary_model_{idx}_tensor_parallel_size"] = 1
        st.session_state[f"auxiliary_model_{idx}_gpu_memory_utilization"] = 0.9
        st.session_state[f"auxiliary_model_{idx}_seed"] = 42
        st.session_state[f"auxiliary_model_{idx}_use_v1"] = True
        st.session_state[f"auxiliary_model_{idx}_enforce_eager"] = True
        st.session_state["_auxiliary_models_num"] += 1
        set_trainer_gpu_num()
    if st.session_state["_auxiliary_models_num"] > 0:
        tabs = st.tabs(
            [f"Auxiliary Model {i + 1}" for i in range(st.session_state["_auxiliary_models_num"])]
        )
        for idx, tab in enumerate(tabs):
            with tab:
                _set_auxiliary_model_idx(idx)


@CONFIG_GENERATORS.register_check()
def check_auxiliary_models(unfinished_fields: set, key: str):
    if st.session_state["trainer_gpu_num"] <= 0:
        unfinished_fields.add("engine_num")
        unfinished_fields.add("tensor_parallel_size")
        st.warning(
            "Please check the settings of each `engine_num` and `tensor_marallel_size` to ensure that at least one GPU is reserved for the `trainer`."
        )
    elif (
        st.session_state["node_num"] > 1
        and st.session_state["trainer_gpu_num"] % st.session_state["gpu_per_node"] != 0
    ):
        unfinished_fields.add("engine_num")
        unfinished_fields.add("tensor_parallel_size")
        st.warning(
            "When `node_num > 1`, please check the settings of each `engine_num` and `tensor_marallel_size` to ensure that the number of GPUs reserved for the `trainer` is divisible by `gpu_per_node`"
        )


# Synchronizer Configs


@CONFIG_GENERATORS.register_config(
    default_value=SyncMethod.NCCL.value,
    visible=explorer_visible,
    other_configs={"_not_dpo_sync_method": SyncMethod.NCCL.value},
)
def set_sync_method(**kwargs):
    key = kwargs.get("key")
    if st.session_state["algorithm_type"] == "dpo":
        st.session_state[key] = SyncMethod.CHECKPOINT.value
        disabled = True
    else:
        st.session_state[key] = st.session_state["_not_dpo_sync_method"]
        disabled = False

    def on_change():
        if st.session_state["algorithm_type"] != "dpo":
            st.session_state["_not_dpo_sync_method"] = st.session_state[key]

    st.selectbox(
        "Sync Method",
        [sync_method.value for sync_method in SyncMethod],
        help="""`nccl`: the explorer and trainer sync model weights once every `sync_interval` steps.

`checkpoint`: the trainer saves the model checkpoint, and the explorer loads it at `sync_interval`.""",
        disabled=disabled,
        on_change=on_change,
        **kwargs,
    )


@CONFIG_GENERATORS.register_config(default_value=10, visible=explorer_visible)
def set_sync_interval(**kwargs):
    st.number_input(
        "Sync Interval",
        min_value=1,
        help="""The step interval at which the `explorer` and `trainer` synchronize model weight.""",
        **kwargs,
    )


@CONFIG_GENERATORS.register_config(default_value=1200, visible=explorer_visible)
def set_sync_timeout(**kwargs):
    st.number_input(
        "Sync Timeout",
        min_value=1,
        help="The timeout value for the synchronization operation.",
        **kwargs,
    )
