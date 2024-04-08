python ../main_transductive.py \
    --device -1 \
	--n_layers 2 \
	--n_hid 512 \
	--num_heads 4 \
	--max_epoch 1500 \
	--lr 0.001 \
	--weight_decay 0 \
	--activation relu \
	--optimizer adam \
	--drop_edge_rate 0.0 \
	--loss_fn "sce" \
	--seeds 10 0\
	--replace_rate 0.05 \
	--alpha_l 3 \
	--save_model 
