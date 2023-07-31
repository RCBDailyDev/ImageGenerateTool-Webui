




def gen_image(gen_info):
    try:
        from modules.processing import StableDiffusionProcessingTxt2Img
        from modules import shared as auto_shared

        p = StableDiffusionProcessingTxt2Img(
            sampler_name='Euler a',
            sd_model=auto_shared.sd_model,
            prompt=gen_info.prompt,
            negative_prompt=n_prompt,
            batch_size=batch,
            steps=steps,
            cfg_scale=cfg,
            width=width,
            height=height,
            do_not_save_grid=True,
            do_not_save_samples=True,
            do_not_reload_embeddings=True
        )
        processed = process_txt2img(p)
        p.close()
        output = processed
    except Exception as e:
        import traceback
        traceback.print_exception(e)
    return output