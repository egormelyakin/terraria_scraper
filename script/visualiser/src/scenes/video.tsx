import {OffthreadVideo, AbsoluteFill} from 'remotion';
import {staticFile} from 'remotion';

export const Video: React.FC<{
	path: string;
	length: number;
}> = ({path, length}) => {
	// return (
	// 	<div
	// 		style={{
	// 			overflow: 'hidden',
	// 			backgroundColor: '#666',
	// 			display: 'flex',
	// 			alignItems: 'center',
	// 			justifyContent: 'center',
	// 			fontSize: '1.5rem',
	// 			position: 'absolute',
	// 			width: '100%',
	// 			height: '100%',
	// 			zIndex: -1,
	// 		}}
	// 	>
	// 		{path}
	// 	</div>
	// );
	return (
		<div
			style={{
				position: 'absolute',
				height: '100%',
				zIndex: -1,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
			}}
		>
			<OffthreadVideo
				style={{
					height: '100%',
					width: '100%',
					objectFit: 'cover',
					imageRendering: 'pixelated',
					// position: 'absolute',
					// zIndex: -1,
				}}
				src={staticFile(path)}
				startFrom={(360 - length) / 2}
			/>
		</div>
	);
};
