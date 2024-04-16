import {continueRender, delayRender, staticFile} from 'remotion';
import {Video} from './video';

const waitForFont = delayRender();
const font = new FontFace(
	`Terraria`,
	`url('${staticFile('ProximaNova-Semibold.ttf')}')`
);
font
	.load()
	.then(() => {
		document.fonts.add(font);
		continueRender(waitForFont);
	})
	.catch((err) => console.log('Error loading font', err));

export const Option: React.FC<{
	optionData: {
		video: string;
		content: {
			note_type: string;
			note_text: string;
			note_image: string | null;
			note_count: number;
		}[];
	};
	pos_type: string;
	length: number;
	stepIndex?: number;
}> = ({optionData, pos_type, length, stepIndex}) => {
	return (
		<div
			style={{
				position: 'relative',
				display: 'flex',
				flexDirection: 'column',
				alignItems: 'start',
				justifyContent: 'end',
				overflow: 'hidden',
				// border: '1px solid #111',
			}}
		>
			<Note
				noteData={optionData.content}
				pos_type={pos_type}
				stepIndex={stepIndex}
			/>
			<Video path={optionData.video} length={length} />
		</div>
	);
};

export const Note: React.FC<{
	noteData: {
		note_type: string;
		note_text: string;
		note_image: string | null;
		note_count: number;
	}[];
	pos_type: string;
	stepIndex?: number;
}> = ({noteData, pos_type, stepIndex}) => {
	let children = noteData.map((note, index) => {
		if (note.note_type === 'Text') {
			return <TextNoteItem key={index} noteData={note} />;
		} else if (note.note_type === 'Image') {
			return <ImageNoteItem key={index} noteData={note} />;
		} else {
			return <></>;
		}
	});

	if (stepIndex !== undefined) {
		const indNote = (
			<TextNoteItem
				noteData={{
					note_type: 'Text',
					note_text: `${stepIndex + 1}.`,
					note_image: null,
					note_count: 1,
				}}
			/>
		);
		children = [indNote, ...children];
	}

	return (
		<div
			style={{
				position: 'absolute',
				width: '100%',
				height: '100%',
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
			}}
		>
			<div
				style={{
					fontSize: '2rem',
					fontFamily: 'Terraria',
					backgroundColor: '#fff',
					maxWidth: '70%',
					color: '#000',
					padding: '1rem 1.5rem',
					display: 'flex',
					flexWrap: 'wrap',
					alignItems: 'center',
					justifyContent: 'center',
					rowGap: '.5rem',
					columnGap: '.75rem',
					position: 'absolute',
					top:
						pos_type === 'single' ? '57%' : pos_type === 'top' ? 'auto' : '1%',
					bottom:
						pos_type === 'single' ? '' : pos_type === 'top' ? '1%' : 'auto',
					borderRadius: '1rem',
				}}
			>
				{children}
			</div>
		</div>
	);
};

export const TextNoteItem: React.FC<{
	noteData: {
		note_type: string;
		note_text: string;
		note_image: string | null;
		note_count: number;
	};
}> = ({noteData}) => {
	return (
		<span
			style={{
				display: 'inline-block',
				// marginRight: '1rem',
			}}
		>
			{noteData.note_text}
		</span>
	);
};

export const ImageNoteItem: React.FC<{
	noteData: {
		note_type: string;
		note_text: string;
		note_image: string | null;
		note_count: number;
	};
}> = ({noteData}) => {
	let text = noteData.note_text;
	if (noteData.note_count > 1) {
		text += ` x${noteData.note_count}`;
	}

	const children = [];
	if (noteData.note_image) {
		children.push(
			<img
				style={{
					maxHeight: '60%',
					height: '60%',
					maxWidth: '3rem',
					objectFit: 'contain',
				}}
				src={staticFile(noteData.note_image!)}
			/>
		);
	}
	children.push(
		<p
			style={{
				fontSize: '1.5rem',
				margin: 0,
			}}
		>
			{text}
		</p>
	);
	const span = (
		<span
			style={{
				backgroundColor: '#bbb',
				height: '3rem',
				padding: '0rem 1rem',
				gap: '1rem',
				display: 'inline-flex',
				alignItems: 'center',
				justifyContent: 'center',
				overflow: 'hidden',
				borderRadius: '.5rem',
			}}
		>
			{children}
		</span>
	);
	return span;
};
