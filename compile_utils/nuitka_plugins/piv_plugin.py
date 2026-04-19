from nuitka.plugins.PluginBase import NuitkaPluginBase


class PivNuitkaPlugin(NuitkaPluginBase):
    # Derive from filename, but can and should also be explicit.
    plugin_name = "PivPlugin"

    def onModuleEncounter(  # noqa: N802
        self, using_module_name, module_name, module_filename, module_kind
    ) -> None:
        print(
            "onModuleEncounter",
            using_module_name,
            module_name,
            module_filename,
            module_kind,
        )

    def onModuleRecursion(
        self,
        module_name,
        module_filename,
        module_kind,
        using_module_name,
        source_ref,
        reason,
    ):
        return None
