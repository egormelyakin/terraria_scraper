import {Option, ImageNoteItem} from './scenes/option';
import {Sequence} from 'remotion';

type item = {
	item: string;
	image: string;
	video: string;
	guide: {
		item: string;
		image: string | null;
		options: {
			video: string;
			type: string;
			content: {
				note_type: string;
				note_text: string;
				note_image: string | null;
				note_count: number;
			}[];
		}[];
	}[];
};

export const MyComposition: React.FC<item> = (item) => {
	const steps = item.guide;
	const children: JSX.Element[] = [];
	let length = 0;

	const totalOptions = steps.reduce((acc, step) => {
		return acc + step.options.length;
	}, 0);
	const totalLength = 59 * 60;
	let optionLength: number;
	let introOutroLength: number;

	if (Math.floor(totalLength / (totalOptions + 2)) > 120) {
		optionLength = Math.floor(totalLength / (totalOptions + 2));
		optionLength = Math.min(optionLength, 180);
		introOutroLength = optionLength;
	} else {
		introOutroLength = 120;
		optionLength = Math.floor((totalLength - 240) / totalOptions);
	}

	const intro = {
		item: item.item,
		image: item.image,
		options: [
			{
				video: item.video,
				type: 'text',
				content: [
					{
						note_type: 'Text',
						note_text: 'How to get',
						note_image: null,
						note_count: 1,
					},
					{
						note_type: 'Image',
						note_text: item.item,
						note_image: item.image,
						note_count: 1,
					},
					{
						note_type: 'Text',
						note_text: 'in Terraria',
						note_image: null,
						note_count: 1,
					},
				],
			},
		],
	};
	children.push(
		<Sequence key={-1} from={0} durationInFrames={introOutroLength}>
			<Step stepData={intro} length={introOutroLength} />
		</Sequence>
	);
	length += introOutroLength;

	// let optionLength = 180;
	steps.forEach((step, index) => {
		const duration = step.options.length * optionLength;
		let overlayData = [step];
		if (index !== steps.length - 1) {
			overlayData.push(steps[steps.length - 1]);
		}
		children.push(
			<Sequence key={index} from={length} durationInFrames={duration}>
				{/* <Overlay stepData={overlayData} /> */}
				<Step stepData={step} length={duration} stepIndex={index} />
			</Sequence>
		);
		length += duration;
	});

	const outro = {
		item: item.item,
		image: item.image,
		options: [
			{
				video: item.video,
				type: 'text',
				content: [
					{
						note_type: 'Text',
						note_text: 'Done!',
						note_image: null,
						note_count: 1,
					},
					{
						note_type: 'Text',
						note_text: 'Full video on',
						note_image: null,
						note_count: 1,
					},
					{
						note_type: 'Image',
						note_text: 'psnk',
						note_image: 'images/youtube.png',
						note_count: 1,
					},
				],
			},
		],
	};
	children.push(
		<Sequence
			key={steps.length}
			from={length}
			durationInFrames={introOutroLength}
		>
			{/* <Overlay stepData={[outro]} /> */}
			<Step stepData={outro} length={introOutroLength} />
		</Sequence>
	);
	length += 180;

	return <>{children}</>;
};

export const TimelineLength = (item: item) => {
	const steps = item.guide;
	const totalOptions = steps.reduce((acc, step) => {
		return acc + step.options.length;
	}, 0);
	const totalLength = 59 * 60;
	let optionLength: number;
	let introOutroLength: number;

	if (Math.floor(totalLength / (totalOptions + 2)) > 120) {
		optionLength = Math.floor(totalLength / (totalOptions + 2));
		optionLength = Math.min(optionLength, 180);
		introOutroLength = optionLength;
	} else {
		introOutroLength = 120;
		optionLength = Math.floor((totalLength - 240) / totalOptions);
	}

	let length = introOutroLength;
	steps.forEach((step, index) => {
		length += step.options.length * optionLength;
	});
	length += introOutroLength;
	return length;
	// return 180 * item.guide.length + 180;
};

export const Step: React.FC<{
	stepData: item['guide'][0];
	length: number;
	stepIndex?: number;
}> = ({stepData, length, stepIndex}) => {
	// const children = stepData.options.map((option, index) => {
	// 	return <Option key={index} optionData={option} />;
	// });

	let children: JSX.Element[] = [];
	if (stepData.options.length === 1) {
		children = [
			<Option
				optionData={stepData.options[0]}
				pos_type="single"
				length={length}
				stepIndex={stepIndex}
			/>,
		];
	} else if (stepData.options.length == 2) {
		children = [
			<Option
				optionData={stepData.options[0]}
				pos_type="top"
				length={length}
				stepIndex={stepIndex}
			/>,
			<Option
				optionData={stepData.options[1]}
				pos_type="bottom"
				length={length}
				stepIndex={stepIndex}
			/>,
		];
	} else {
		children = [
			<Option
				optionData={stepData.options[0]}
				pos_type="top"
				length={length}
				stepIndex={stepIndex}
			/>,
			<Option
				optionData={stepData.options[1]}
				pos_type="single"
				length={length}
				stepIndex={stepIndex}
			/>,
			<Option
				optionData={stepData.options[2]}
				pos_type="bottom"
				length={length}
				stepIndex={stepIndex}
			/>,
		];
	}

	return (
		<div
			style={{
				display: 'grid',
				width: '100%',
				height: '100%',
				gridTemplateRows: `repeat(${stepData.options.length}, 1fr)`,
			}}
		>
			{children}
		</div>
	);
};

export const Overlay: React.FC<{
	stepData: (item['guide'][0] | null)[];
}> = ({stepData}) => {
	return (
		<div
			style={{
				position: 'absolute',
				fontFamily: 'Terraria',
				color: '#ddd',
				fontSize: '1.5rem',
				margin: '2rem',
				display: 'flex',
				flexDirection: 'column',
				alignItems: 'start',
				gap: '.25rem',
			}}
		>
			{stepData[1] ? (
				<ImageNoteItem
					noteData={{
						note_type: 'Image',
						note_text: stepData[1].item,
						note_image: stepData[1].image,
						note_count: 1,
					}}
				></ImageNoteItem>
			) : (
				<></>
			)}
			{stepData[0] ? (
				<ImageNoteItem
					noteData={{
						note_type: 'Image',
						note_text: stepData[0].item,
						note_image: stepData[0].image,
						note_count: 1,
					}}
				></ImageNoteItem>
			) : (
				<></>
			)}
		</div>
	);
};
