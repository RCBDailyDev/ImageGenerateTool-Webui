from modules import processing, shared
from modules.processing import Processed


def gen_image(gen_info):
    try:
        from modules.processing import StableDiffusionProcessingTxt2Img
        from modules import shared as auto_shared

        p = StableDiffusionProcessingTxt2Img(
            sampler_name=gen_info['sampler'],
            sd_model=auto_shared.sd_model,
            prompt=gen_info['prompt'],
            negative_prompt=['neg_prompt'],
            batch_size=1,
            steps=gen_info['sample_step'],
            cfg_scale=gen_info['cfg_scale'],
            width=gen_info['img_width'],
            height=gen_info['img_width'],
            do_not_save_grid=True,
            do_not_save_samples=True,
            do_not_reload_embeddings=True
        )
        p.seed = -1
        if type(p.prompt) == list:
            p.all_prompts = [shared.prompt_styles.apply_styles_to_prompt(x, p.styles) for x in p.prompt]
        else:
            p.all_prompts = [shared.prompt_styles.apply_styles_to_prompt(p.prompt, p.styles)]

        if type(p.negative_prompt) == list:
            p.all_negative_prompts = [shared.prompt_styles.apply_negative_styles_to_prompt(x, p.styles) for x in
                                      p.negative_prompt]
        else:
            p.all_negative_prompts = [shared.prompt_styles.apply_negative_styles_to_prompt(p.negative_prompt, p.styles)]

        processed: Processed = processing.process_images(p)
        output = processed.images
    except Exception as e:
        import traceback
        output = None
        traceback.print_exception(e)
    return output
