# Area of technical AI safety work you're excited about

I'm most excited about empirically measuring the structure of moral reasoning in LLMs—specifically, detecting alignment failures through symmetry violations before they manifest as harmful outputs.

The core insight is borrowed from physics: Noether's theorem tells us that symmetries imply conservation laws. Applied to normative reasoning, this means that if an AI system's ethical judgments are coherent, semantically equivalent inputs should produce equivalent outputs. When they don't, we've detected a measurable defect—a crack in the alignment surface.

My SQND (Stratified Quantum Normative Dynamics) experiments operationalize this. I present models with ethical scenarios, apply systematic transformations (reframing, reordering, perspective shifts), and measure whether judgments remain consistent. The results are striking: current LLMs exhibit reproducible symmetry violations under specific perturbation classes. These aren't random errors—they follow patterns that suggest exploitable weaknesses in how models represent normative concepts.

What excites me is that this approach is *falsifiable* and *actionable*. Unlike debates about whether models "truly understand" ethics, symmetry violations are measurable. A Bond Index score tells you something concrete: this system's moral reasoning breaks under these specific conditions. That's information you can use for deployment decisions, targeted training interventions, or red-teaming.

The deeper question this opens: do these violations reflect fundamental limitations in how current architectures represent normative reasoning, or are they artifacts of training that could be resolved? Either answer would be valuable. If fundamental, it tells us something important about what alignment techniques we need. If resolvable, we have a metric to optimize against.

I want to scale these experiments—more models, more systematic coverage of the perturbation space, more rigorous statistical characterization. The fellowship's compute and mentorship could help determine whether this approach generalizes into a practical alignment verification tool or reveals its own limitations. Both outcomes advance the field.
