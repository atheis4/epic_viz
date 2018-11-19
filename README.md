# epic_viz
A Django powered web app to track inputs to the Epi(demiology) Computation process at IHME.


# ABOUT
Epic Viz provides a web app interface for viewing the status of the model versions for every input modelable entity to the Epi Computation pipeline.

Hosted on an internal Rancher server and containerized with Docker, the web app allows researchers and disease modelers to quickly view whether their models are up to date, or can be rerun with new input data.

The models versions are tracked by modelable entity. A status of green means that the model is marked best and is up to date. Yellow means that a marked best model has new data available and is ready to be rerun. Orange means that there is no model marked best for the corresponding modelable entity for the current GBD round. And Red means that there is no model for the given modelable entity id.

*Currently this web app is only available on internal IHME servers*
