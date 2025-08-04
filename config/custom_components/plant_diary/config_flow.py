"""Config flow for the Plant Diary integration."""

from homeassistant import config_entries

from .const import DOMAIN


class PlantDiaryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for the Plant Diary integration."""

    async def async_step_user(self, user_input=None):
        """Handle the user step in the configuration flow."""
        existing_entries = self._async_current_entries()
        if existing_entries:
            return self.async_abort(reason="single_instance_allowed")

        # No configuration form is needed for this integration
        return self.async_create_entry(title="Plant Diary", data={})
